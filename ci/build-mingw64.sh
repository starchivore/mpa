#!/bin/bash -e

prefix_dir=$PWD/mingw_prefix
mkdir -p "$prefix_dir"
ln -snf . "$prefix_dir/usr"
ln -snf . "$prefix_dir/local"

wget="wget -nc --progress=bar:force"
gitclone="git clone --depth=10 --recursive"
commonflags="--disable-static --enable-shared"

export PKG_CONFIG_SYSROOT_DIR="$prefix_dir"
export PKG_CONFIG_LIBDIR="$PKG_CONFIG_SYSROOT_DIR/lib/pkgconfig"

# -posix is Ubuntu's variant with pthreads support
export CC=$TARGET-gcc-posix
export CXX=$TARGET-g++-posix
export AR=$TARGET-ar
export NM=$TARGET-nm
export RANLIB=$TARGET-ranlib

export CFLAGS="-O2 -pipe -Wall -D_FORTIFY_SOURCE=2"
export LDFLAGS="-fstack-protector-strong"

fam=x86_64
[[ "$TARGET" == "i686-"* ]] && fam=x86
cat >"$prefix_dir/crossfile" <<EOF
[built-in options]
buildtype = 'release'
wrap_mode = 'nodownload'
[binaries]
c = '${CC}'
cpp = '${CXX}'
ar = '${AR}'
strip = '${TARGET}-strip'
pkgconfig = 'pkg-config'
windres = '${TARGET}-windres'
[host_machine]
system = 'windows'
cpu_family = '${fam}'
cpu = '${TARGET%%-*}'
endian = 'little'
EOF

function builddir () {
    [ -d "$1/builddir" ] && rm -rf "$1/builddir"
    mkdir -p "$1/builddir"
    pushd "$1/builddir"
}

function makeplusinstall () {
    if [ -f build.ninja ]; then
        ninja
        DESTDIR="$prefix_dir" ninja install
    else
        make -j$(nproc)
        make DESTDIR="$prefix_dir" install
    fi
}

function gettar () {
    name="${1##*/}"
    [ -d "${name%%.*}" ] && return 0
    $wget "$1"
    tar -xaf "$name"
}

## ffmpeg
if [ ! -e "$prefix_dir/lib/libavcodec.dll.a" ]; then
    [ -d ffmpeg ] || $gitclone https://github.com/FFmpeg/FFmpeg.git ffmpeg
    builddir ffmpeg
    ../configure --pkg-config=pkg-config --target-os=mingw32 \
        --enable-cross-compile --cross-prefix=$TARGET- --arch=${TARGET%%-*} \
        $commonflags \
        --disable-{doc,programs,muxers,encoders,devices}
    makeplusinstall
    popd
fi

## mpv

[ -z "$1" ] && exit 0

CFLAGS+=" -I'$prefix_dir/include'"
LDFLAGS+=" -L'$prefix_dir/lib'"
export CFLAGS LDFLAGS
rm -rf build

if [ "$1" = "meson" ]; then
    meson setup build --cross-file "$prefix_dir/crossfile" \
        --buildtype debugoptimized \
        -D{libmpv,build-date,tests,ta-leak-report}=false -Dlua=disabled \
        -D{cdda,cplugins,dvbin,dvdnav,iconv,javascript,lcms2,libarchive,libavdevice,libbluray,pthread-debug,rubberband,sdl2,sdl2-gamepad,stdatomic,uchardet,uwp,vapoursynth,vector,win32-internal-pthreads,zimg,zlib,alsa,audiounit,coreaudio,jack,openal,opensles,oss-audio,pipewire,pulse,sdl2-audio,sndio,caca,cocoa,d3d11,direct3d,drm,egl,egl-android,egl-angle,egl-angle-lib,egl-angle-win32,egl-drm,egl-wayland,egl-x11,gbm,gl,gl-cocoa,gl-dxinterop,gl-win32,gl-x11,jpeg,libplacebo,rpi,sdl2-video,shaderc,sixel,spirv-cross,plain-gl,vdpau,vdpau-gl-x11,vaapi,vaapi-drm,vaapi-wayland,vaapi-x11,vaapi-x-egl,vulkan,wayland,x11,xv,android-media-ndk,cuda-hwaccel,cuda-interop,d3d-hwaccel,d3d9-hwaccel,gl-dxinterop-d3d9,ios-gl,rpi-mmal,videotoolbox-gl,macos-10-11-features,macos-10-12-2-features,macos-10-14-features,macos-cocoa-cb,macos-media-player,macos-touchbar,swift-build,swift-flags,html-build,manpage-build,pdf-build}=disabled

    ninja -C build --verbose
elif [ "$1" = "waf" ]; then
    PKG_CONFIG=pkg-config ./waf configure \
        --disable-libmpv-shared --disable-libmpv-static --disable-build-date --disable-debug-build --disable-tests --disable-manpage-build --disable-html-build --disable-pdf-build --disable-cplugins --disable-vector --disable-clang-database --disable-swift-static --disable-android --disable-android-media-ndk --disable-tvos --disable-gl --disable-swift --disable-uwp --disable-win32-internal-pthreads --disable-pthread-debug --disable-stdatomic --disable-iconv --disable-lua --disable-javascript --disable-zlib --disable-libbluray --disable-dvdnav --disable-cdda --disable-uchardet --disable-rubberband --disable-zimg --disable-lcms2 --disable-vapoursynth --disable-libarchive --disable-dvbin --disable-sdl2 --disable-sdl2-gamepad --disable-libavdevice --disable-sdl2-audio --disable-oss-audio --disable-pipewire --disable-sndio --disable-pulse --disable-jack --disable-openal --disable-opensles --disable-alsa --disable-coreaudio --disable-audiounit --disable-sdl2-video --disable-cocoa --disable-drm --disable-gbm --disable-wayland --disable-x11 --disable-xv --disable-rpi --disable-vdpau --disable-gl-x11 --disable-vaapi --disable-vaapi-x11 --disable-vaapi-wayland --disable-vaapi-drm --disable-vaapi-x-egl --disable-caca --disable-jpeg --disable-direct3d --disable-shaderc --disable-spirv-cross --disable-d3d11 --disable-ios-gl --disable-plain-gl --disable-gl --disable-libplacebo --disable-vulkan --disable-sixel --disable-videotoolbox-gl --disable-d3d-hwaccel --disable-d3d9-hwaccel --disable-cuda-hwaccel --disable-cuda-interop --disable-rpi-mmal --disable-macos-touchbar --disable-macos-10-11-features --disable-macos-10-12-2-features --disable-macos-10-14-features --disable-macos-media-player --disable-macos-cocoa-cb

    ./waf build --verbose
fi

if [ "$2" = pack ]; then
    mkdir -p artifact
    echo "Copying:"
    cp -pv build/mpv.{com,exe} "$prefix_dir/bin/"*.dll artifact/
    # ship everything and the kitchen sink
    shopt -s nullglob
    for file in /usr/lib/gcc/$TARGET/*-posix/*.dll /usr/$TARGET/lib/*.dll; do
        cp -pv "$file" artifact/
    done
    echo "Archiving:"
    pushd artifact
    zip -9r "../mpv-git-$(date +%F)-$(git rev-parse --short HEAD)-${TARGET%%-*}.zip" -- *
    popd
fi
