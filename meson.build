project('mpv',
        'c',
        license: ['GPL2+', 'LGPL2.1+'],
        version: files('./VERSION'),
        meson_version: '>=0.60.3',
        default_options: [
            'buildtype=debugoptimized',
            'b_lundef=false',
            'c_std=c11',
            'warning_level=1',
        ]
)

build_root = meson.project_build_root()
source_root = meson.project_source_root()
python = find_program('python3')

# ffmpeg
libavcodec = dependency('libavcodec', version: '>= 58.134.100')
libavfilter = dependency('libavfilter', version: '>= 7.110.100')
libavformat = dependency('libavformat', version: '>= 58.76.100')
libavutil = dependency('libavutil', version: '>= 56.70.100')
libswresample = dependency('libswresample', version: '>= 3.9.100')
libswscale = dependency('libswscale', version: '>= 5.9.100')

pthreads = dependency('threads')

# the dependency order of libass -> ffmpeg is necessary due to
# static linking symbol resolution between fontconfig and MinGW
dependencies = [libavcodec,
                libavfilter,
                libavformat,
                libavutil,
                libswresample,
                libswscale,
                pthreads]

# Keeps track of all enabled/disabled features
features = {
    'debug': get_option('debug'),
    'ffmpeg': true,
    'gpl': get_option('gpl'),
    'jpegxl': libavformat.version().version_compare('>= 59.27.100'),
    'libass': false,
    'threads': true,
}


# generic sources
sources = files(
    ## Audio
    'audio/aframe.c',
    'audio/chmap.c',
    'audio/chmap_sel.c',
    'audio/decode/ad_lavc.c',
    'audio/decode/ad_spdif.c',
    'audio/filter/af_drop.c',
    'audio/filter/af_format.c',
    'audio/filter/af_lavcac3enc.c',
    'audio/filter/af_scaletempo.c',
    'audio/filter/af_scaletempo2.c',
    'audio/filter/af_scaletempo2_internals.c',
    'audio/fmt-conversion.c',
    'audio/format.c',
    'audio/out/ao.c',
    'audio/out/ao_lavc.c',
    'audio/out/ao_null.c',
    'audio/out/ao_pcm.c',
    'audio/out/buffer.c',

    ## Core
    'common/av_common.c',
    'common/av_log.c',
    'common/codecs.c',
    'common/common.c',
    'common/encode_lavc.c',
    'common/msg.c',
    'common/playlist.c',
    'common/recorder.c',
    'common/stats.c',
    'common/tags.c',
    'common/version.c',

    ## Demuxers
    'demux/codec_tags.c',
    'demux/cue.c',
    'demux/cache.c',
    'demux/demux.c',
    'demux/demux_cue.c',
    'demux/demux_disc.c',
    'demux/demux_edl.c',
    'demux/demux_lavf.c',
    'demux/demux_mf.c',
    'demux/demux_mkv.c',
    'demux/demux_mkv_timeline.c',
    'demux/demux_null.c',
    'demux/demux_playlist.c',
    'demux/demux_raw.c',
    'demux/demux_timeline.c',
    'demux/ebml.c',
    'demux/packet.c',
    'demux/timeline.c',

    ## Filters
    'filters/f_async_queue.c',
    'filters/f_autoconvert.c',
    'filters/f_auto_filters.c',
    'filters/f_decoder_wrapper.c',
    'filters/f_demux_in.c',
    'filters/f_hwtransfer.c',
    'filters/f_lavfi.c',
    'filters/f_output_chain.c',
    'filters/f_swresample.c',
    'filters/f_swscale.c',
    'filters/f_utils.c',
    'filters/filter.c',
    'filters/frame.c',
    'filters/user_filters.c',

    ## Input
    'input/cmd.c',
    'input/event.c',
    'input/input.c',
    'input/ipc.c',
    'input/keycodes.c',

    ## Misc
    'misc/bstr.c',
    'misc/charset_conv.c',
    'misc/dispatch.c',
    'misc/json.c',
    'misc/natural_sort.c',
    'misc/node.c',
    'misc/random.c',
    'misc/rendezvous.c',
    'misc/thread_pool.c',
    'misc/thread_tools.c',

    ## Options
    'options/m_config_core.c',
    'options/m_config_frontend.c',
    'options/m_option.c',
    'options/m_property.c',
    'options/options.c',
    'options/parse_commandline.c',
    'options/parse_configfile.c',
    'options/path.c',

    ## Player
    'player/audio.c',
    'player/client.c',
    'player/command.c',
    'player/configfiles.c',
    'player/external_files.c',
    'player/loadfile.c',
    'player/main.c',
    'player/misc.c',
    'player/osd.c',
    'player/playloop.c',
    'player/screenshot.c',
    'player/scripting.c',
    'player/sub.c',
    'player/video.c',

    ## Streams
    'stream/cookies.c',
    'stream/stream.c',
    'stream/stream_avdevice.c',
    'stream/stream_cb.c',
    'stream/stream_concat.c',
    'stream/stream_edl.c',
    'stream/stream_file.c',
    'stream/stream_lavf.c',
    'stream/stream_memory.c',
    'stream/stream_mf.c',
    'stream/stream_null.c',
    'stream/stream_slice.c',

    ## osdep
    'osdep/io.c',
    'osdep/semaphore_osx.c',
    'osdep/subprocess.c',
    'osdep/threads.c',
    'osdep/timer.c',

    ## tree_allocator
    'ta/ta.c',
    'ta/ta_talloc.c',
    'ta/ta_utils.c'
)


# compiler stuff
cc = meson.get_compiler('c')

flags = ['-D_ISOC99_SOURCE', '-D_GNU_SOURCE',
         '-D_FILE_OFFSET_BITS=64']
link_flags = []

test_flags = ['-Werror=implicit-function-declaration',
              '-Wno-error=deprecated-declarations',
              '-Wno-error=unused-function',
              '-Wempty-body',
              '-Wdisabled-optimization',
              '-Wstrict-prototypes',
              '-Wno-format-zero-length',
              '-Wno-redundant-decls',
              '-Wvla',
              '-Wno-format-truncation',
              '-Wimplicit-fallthrough',
              '-fno-math-errno']

flags += cc.get_supported_arguments(test_flags)

if cc.has_multi_arguments('-Wformat', '-Werror=format-security')
    flags += '-Werror=format-security'
endif

if cc.get_id() == 'gcc'
    gcc_flags = ['-Wundef', '-Wmissing-prototypes', '-Wshadow',
                 '-Wno-switch', '-Wparentheses', '-Wpointer-arith',
                 '-Wno-pointer-sign',
                 # GCC bug 66425
                 '-Wno-unused-result']
    flags += gcc_flags
endif

if cc.get_id() == 'clang'
    clang_flags = ['-Wno-logical-op-parentheses', '-Wno-switch',
                   '-Wno-tautological-compare', '-Wno-pointer-sign',
                   '-Wno-tautological-constant-out-of-range-compare']
    flags += clang_flags
endif

darwin = host_machine.system() == 'darwin'
win32 = host_machine.system() == 'cygwin' or host_machine.system() == 'windows'
posix = not win32
features += {'posix': posix}
features += {'dos-paths': win32, 'win32': win32}

mswin_flags = ['-D_WIN32_WINNT=0x0602', '-DUNICODE', '-DCOBJMACROS',
               '-DINITGUID', '-U__STRICT_ANSI__']

if host_machine.system() == 'windows'
    flags += [mswin_flags, '-D__USE_MINGW_ANSI_STDIO=1']
endif

if host_machine.system() == 'cygwin'
    flags += [mswin_flags, '-mwin32']
endif

noexecstack = false
if cc.has_link_argument('-Wl,-z,noexecstack')
    link_flags += '-Wl,-z,noexecstack'
    noexecstack = true
endif

if cc.has_link_argument('-Wl,--nxcompat,--no-seh,--dynamicbase')
    link_flags += '-Wl,--nxcompat,--no-seh,--dynamicbase'
    noexecstack = true
endif

features += {'noexecstack': noexecstack}

features += {'build-date': get_option('build-date')}
if not features['build-date']
    flags += '-DNO_BUILD_TIMESTAMPS'
endif

features += {'ta-leak-report': get_option('ta-leak-report')}

libdl_dep = cc.find_library('dl', required: false)
features += {'libdl': cc.has_function('dlopen', dependencies: libdl_dep, prefix: '#include <dlfcn.h>')}
if features['libdl']
    dependencies += libdl_dep
endif

cplugins = get_option('cplugins').require(
    features['libdl'] and not win32 and cc.has_link_argument('-rdynamic'),
    error_message: 'cplugins not supported by the os or compiler!',
)
features += {'cplugins': cplugins.allowed()}
if features['cplugins']
    link_flags += '-rdynamic'
endif

features += {'tests': get_option('tests')}
if features['tests']
    sources += files('test/chmap.c',
                     'test/gl_video.c',
                     'test/img_format.c',
                     'test/json.c',
                     'test/linked_list.c',
                     'test/paths.c',
                     'test/scale_sws.c',
                     'test/scale_test.c',
                     'test/tests.c')
endif

# Note: this include is only used for windows pthreads and
# must be accompanied immediately by the following flags.
# This currently works because these are the last flags set
# in the build for windows. Adding any new flags after this
# will probably break something.
includedir = []
win32_pthreads = get_option('win32-internal-pthreads').require(
    win32 and not posix,
    error_message: 'the os is not win32!',
)
features += {'win32-internal-pthreads': win32_pthreads.allowed()}
if features['win32-internal-pthreads']
    flags += ['-isystem', '-I', '-DIN_WINPTHREAD']
    # Note: Adding this include causes POSIX_TIMERS to be defined for
    # unclear reasons (some confusion with <pthread.h> probably).
    # Hack around it by using HAVE_WIN32_INTERNAL_PTHREADS.
    includedir += include_directories('osdep/win32/include')
    sources += files('osdep/win32/pthread.c')
endif

pthread_debug = get_option('pthread-debug').require(
    win32_pthreads.disabled(),
    error_message: 'win32-internal-pthreads was found!',
)
features += {'pthread-debug': pthread_debug.allowed()}
if features['pthread-debug']
    flags += '-DMP_PTHREAD_DEBUG'
endif

add_project_arguments(flags, language: 'c')
add_project_link_arguments(link_flags, language: ['c', 'objc'])


# osdep
uwp_opt = get_option('uwp').require(
    not get_option('cplayer'),
    error_message: 'cplayer is not false!',
)
uwp = cc.find_library('windowsapp', required: uwp_opt)
features += {'uwp': uwp.found()}
if features['uwp']
    dependencies += uwp
    sources += files('osdep/path-uwp.c')
endif

features += {'win32-executable': win32 and get_option('cplayer')}
if win32
    sources += files('osdep/timer-win2.c',
                     'osdep/w32_keyboard.c',
                     'osdep/windows_utils.c')
endif

features += {'win32-desktop': win32 and not uwp.found()}
if features['win32-desktop']
    win32_desktop_libs = [cc.find_library('avrt'),
                          cc.find_library('dwmapi'),
                          cc.find_library('gdi32'),
                          cc.find_library('ole32'),
                          cc.find_library('uuid'),
                          cc.find_library('version'),
                          cc.find_library('winmm')]
    dependencies += win32_desktop_libs
    sources += files('input/ipc-win.c',
                     'osdep/main-fn-win.c',
                     'osdep/path-win.c',
                     'osdep/subprocess-win.c',
                     'osdep/terminal-win.c',
                     'video/out/w32_common.c',
                     'video/out/win32/displayconfig.c',
                     'video/out/win32/droptarget.c')
endif

if not posix and not features['win32-desktop']
    sources += files('input/ipc-dummy.c',
                     'osdep/subprocess-dummy.c',
                     'osdep/terminal-dummy.c')
endif

features += {'glob-posix': cc.has_function('glob', prefix: '#include <glob.h>')}

features += {'glob-win32': win32 and not posix}
if features['glob-win32']
    sources += files('osdep/glob-win.c')
endif

features += {'glob': features['glob-posix'] or features['glob-win32']}

features += {'vt.h': cc.has_header_symbol('sys/vt.h', 'VT_GETMODE')}

features += {'consio.h': not features['vt.h'] and cc.has_header_symbol('sys/consio.h', 'VT_GETMODE')}

fragments = join_paths(source_root, 'waftools', 'fragments')

features += {'glibc-thread-name': cc.compiles(files(join_paths(fragments, 'glibc_thread_name.c')),
                                              name: 'glibc-thread-name check') and posix}

features += {'osx-thread-name': false}
if not features['glibc-thread-name']
    features += {'osx-thread-name': cc.compiles(files(join_paths(fragments, 'osx_thread_name.c')),
                                                name: 'osx-thread-name check')}
endif

features += {'bsd-thread-name': false}
if not features['osx-thread-name'] and not features['glibc-thread-name']
    features += {'bsd-thread-name': cc.compiles(files(join_paths(fragments, 'bsd_thread_name.c')),
                                                name: 'bsd-thread-name check')}
endif

features += {'bsd-fstatfs': cc.has_function('fstatfs', prefix: '#include <sys/mount.h>\n#include <sys/param.h>')}

features += {'linux-fstatfs': cc.has_function('fstatfs', prefix: '#include <sys/vfs.h>')}

vector = get_option('vector').require(
    cc.compiles(files(join_paths(fragments, 'vector.c')), name: 'vector check'),
    error_message: 'the compiler does not support gcc vectors!',
)
features += {'vector': vector.allowed()}


# various file generations
tools_directory = join_paths(source_root, 'TOOLS')
file2string = find_program(join_paths(tools_directory, 'file2string.py'))
matroska = find_program(join_paths(tools_directory, 'matroska.py'))
version_py = find_program(join_paths(source_root, 'version.py'))

subdir('generated')
subdir(join_paths('generated', 'etc'))
subdir(join_paths('generated', 'sub'))

if darwin
    subdir(join_paths('generated', 'TOOLS', 'osxbundle', 'mpv.app', 'Contents', 'Resources'))
endif


# misc dependencies
features += {'av-channel-layout': libavutil.version().version_compare('>= 57.24.100')}
if features['av-channel-layout']
    sources += files('audio/chmap_avchannel.c')
endif

iconv = dependency('iconv', required: get_option('iconv'))
features += {'iconv': iconv.found()}
if features['iconv']
    dependencies += iconv
endif

javascript = dependency('mujs', version: '>= 1.0.0', required: get_option('javascript'))
features += {'javascript': javascript.found()}
if features['javascript']
    dependencies += javascript
    sources += files('player/javascript.c',
                     'sub/filter_jsre.c')
    subdir(join_paths('generated', 'player', 'javascript'))
endif

lcms2 = dependency('lcms2', version: '>= 2.6', required: get_option('lcms2'))
features += {'lcms2': lcms2.found()}
if features['lcms2']
    dependencies += lcms2
endif

libarchive = dependency('libarchive', version: '>= 3.4.0', required: get_option('libarchive'))
features += {'libarchive': libarchive.found()}
if features['libarchive']
    dependencies += libarchive
    sources += files('demux/demux_libarchive.c',
                     'stream/stream_libarchive.c')
endif

libavdevice = dependency('libavdevice', version: '>= 58.13.100', required: get_option('libavdevice'))
features += {'libavdevice': libavdevice.found()}
if features['libavdevice']
    dependencies += libavdevice
endif

lua = dependency('', required: false)
lua_opt = get_option('lua')
if lua_opt != 'disabled'
    lua_version = [['lua', ['>=5.1.0', '<5.3.0']], # generic lua.pc
                   ['lua52', '>= 5.2.0'],
                   ['lua5.2', '>= 5.2.0'],
                   ['lua-5.2', '>= 5.2.0'],
                   ['luajit', '>= 2.0.0'],
                   ['lua51', '>= 5.1.0'],
                   ['lua5.1', '>= 5.1.0'],
                   ['lua-5.1', '>= 5.1.0']]
    foreach version : lua_version
        if lua_opt == 'auto' or lua_opt == 'enabled'
            lua = dependency(version[0], version: version[1], required: false)
            if lua.found()
                break
            endif
        elif lua_opt == version[0]
            lua = dependency(version[0], version: version[1])
            if lua.found()
                break
            endif
        endif
    endforeach
endif

features += {'lua': lua.found()}
lua_version = lua.name()
if features['lua']
    dependencies += lua
    sources += files('player/lua.c')
    subdir(join_paths('generated', 'player', 'lua'))
endif
if not features['lua'] and lua_opt == 'enabled'
     error('lua enabled but no suitable lua version could be found!')
endif

rubberband = dependency('rubberband', version: '>= 1.8.0', required: get_option('rubberband'))
features += {'rubberband': rubberband.found()}
features += {'rubberband-3': rubberband.version().version_compare('>= 3.0.0')}
if features['rubberband']
    dependencies += rubberband
    sources += files('audio/filter/af_rubberband.c')
endif

sdl2 = dependency('sdl2', required: get_option('sdl2'))
features += {'sdl2': sdl2.found()}
if features['sdl2']
    dependencies += sdl2
endif

sdl2_gamepad = get_option('sdl2-gamepad').require(
    features['sdl2'],
    error_message: 'sdl2 was not found!',
)
features += {'sdl2-gamepad': sdl2_gamepad.allowed()}
if features['sdl2-gamepad']
    sources += files('input/sdl_gamepad.c')
endif

stdatomic_dep = cc.find_library('atomic', required: false)
features += {'stdatomic': cc.has_header_symbol('stdatomic.h', 'atomic_int', dependencies: stdatomic_dep,
                                               required: get_option('stdatomic'))}
if features['stdatomic']
    dependencies += stdatomic_dep
endif

uchardet_opt = get_option('uchardet').require(
    features['iconv'],
    error_message: 'iconv was not found!',
)
uchardet = dependency('uchardet', required: uchardet_opt)
features += {'uchardet': uchardet.found()}
if features['uchardet']
    dependencies += uchardet
endif

vapoursynth = dependency('vapoursynth', version: '>= 24', required: get_option('vapoursynth'))
vapoursynth_script = dependency('vapoursynth-script', version: '>= 23',
                                required: get_option('vapoursynth'))
features += {'vapoursynth': vapoursynth.found() and vapoursynth_script.found()}
if features['vapoursynth']
    dependencies += [vapoursynth, vapoursynth_script]
    sources += files('video/filter/vf_vapoursynth.c')
endif

zimg = dependency('zimg', version: '>= 2.9', required: get_option('zimg'))
features += {'zimg': zimg.found()}
if features['zimg']
    dependencies += zimg
    sources += files('video/filter/vf_fingerprint.c',
                     'video/zimg.c')
    if features['tests']
        sources += files('test/repack.c',
                         'test/scale_zimg.c')
    endif
endif

zlib = dependency('zlib', required: get_option('zlib'))
features += {'zlib': zlib.found()}
if features['zlib']
    dependencies += zlib
endif


# audio output dependencies
alsa = dependency('alsa', version: '>= 1.0.18', required: get_option('alsa'))
features += {'alsa': alsa.found()}
if features['alsa']
    dependencies += alsa
    sources += files('audio/out/ao_alsa.c')
endif

audiounit = {
    'deps': dependency('appleframeworks', modules: ['Foundation', 'AudioToolbox'],
                       required: get_option('audiounit')),
    'symbol': cc.has_header_symbol('AudioToolbox/AudioToolbox.h', 'kAudioUnitSubType_RemoteIO',
                                   required: get_option('audiounit')),
}
features += {'audiounit': audiounit['deps'].found() and audiounit['symbol']}
if features['audiounit']
    dependencies += audiounit['deps']
    sources += files('audio/out/ao_audiounit.m')
endif

coreaudio = dependency('appleframeworks', modules: ['CoreFoundation', 'CoreAudio',
                       'AudioUnit', 'AudioToolbox'], required: get_option('coreaudio'))
features += {'coreaudio': coreaudio.found()}
if features['coreaudio']
    dependencies += coreaudio
    sources += files('audio/out/ao_coreaudio.c',
                     'audio/out/ao_coreaudio_exclusive.c',
                     'audio/out/ao_coreaudio_properties.c')
endif

if features['audiounit'] or features['coreaudio']
    sources += files('audio/out/ao_coreaudio_chmap.c',
                     'audio/out/ao_coreaudio_utils.c')
endif

jack_opt = get_option('jack').require(
    get_option('gpl'),
    error_message: 'the build is not GPL!',
)
jack = dependency('jack', required: jack_opt)
features += {'jack': jack.found()}
if features['jack']
    dependencies += jack
    sources += files('audio/out/ao_jack.c')
endif

openal = dependency('openal', version: '>= 1.13', required: get_option('openal'))
features += {'openal': openal.found()}
if features['openal']
    dependencies += openal
    sources += files('audio/out/ao_openal.c')
endif

opensles = cc.find_library('OpenSLES', required: get_option('opensles'))
features += {'opensles': opensles.found()}
if features['opensles']
    dependencies += opensles
    sources += files('audio/out/ao_opensles.c')
endif

oss_opt = get_option('oss-audio').require(
    get_option('gpl'),
    error_message: 'the build is not GPL!',
)
features += {'oss-audio': cc.has_header_symbol('sys/soundcard.h', 'SNDCTL_DSP_SETPLAYVOL',
                                               required: oss_opt)}
if features['oss-audio']
    sources += files('audio/out/ao_oss.c')
endif

pipewire = dependency('libpipewire-0.3', version: '>= 0.3.19', required: get_option('pipewire'))
features += {'pipewire': pipewire.found()}
if features['pipewire']
    dependencies += pipewire
    sources += files('audio/out/ao_pipewire.c')
endif

pulse = dependency('libpulse', version: '>= 1.0', required: get_option('pulse'))
features += {'pulse': pulse.found()}
if features['pulse']
    dependencies += pulse
    sources += files('audio/out/ao_pulse.c')
endif

sdl2_audio = get_option('sdl2-audio').require(
    features['sdl2'],
    error_message: 'sdl2 was not found!',
)
features += {'sdl2-audio': sdl2_audio.allowed()}
if features['sdl2-audio']
    sources += files('audio/out/ao_sdl.c')
endif

sndio = dependency('sndio', required: get_option('sndio'))
features += {'sndio': sndio.found()}
if features['sndio']
    dependencies += sndio
    sources += files('audio/out/ao_sndio.c')
endif

wasapi = cc.has_header_symbol('audioclient.h', 'IAudioClient', required: get_option('wasapi'))
features += {'wasapi': wasapi}
if features['wasapi']
    sources += files('audio/out/ao_wasapi.c',
                     'audio/out/ao_wasapi_changenotify.c',
                     'audio/out/ao_wasapi_utils.c')
endif


# Currently, we can't easily get every single thing a user might have passed
# on the cli, but we might as well just hardcode a few options (even if they are
# not specifically set) for verbosity's sake.
configuration = 'meson configure build ' + '-Dprefix=' + get_option('prefix') + \
                ' -Dbuildtype=' + get_option('buildtype') + \
                ' -Doptimization=' + get_option('optimization')

features += {'cplayer': get_option('cplayer')}
features += {'libmpv-' + get_option('default_library'): get_option('libmpv')}


# Set config.h
conf_data = configuration_data()
conf_data.set_quoted('CONFIGURATION', configuration)

# Loop over all features in the build, create a define and add them to config.h
feature_keys = []
foreach feature, allowed: features
    define = 'HAVE_@0@'.format(feature.underscorify().to_upper())
    conf_data.set10(define, allowed)
    # special handling for lua
    if feature == 'lua' and allowed
        feature_keys += lua_version
        continue
    endif
    if allowed
        feature_keys += feature
    endif
endforeach


# Script to sort the feature_keys object.
feature_sort = '''
#!/usr/bin/env python3
import sys
features = " ".join(sorted(sys.argv[1:]))
sys.stdout.write(features)
'''
feature_str = run_command(python, '-c', feature_sort, feature_keys, check: true).stdout()
conf_data.set_quoted('FULLCONFIG', feature_str)
conf_data.set_quoted('MPV_CONFDIR', join_paths(get_option('prefix'), get_option('sysconfdir'), 'mpv'))
configure_file(output : 'config.h', configuration : conf_data)
message('List of enabled features: ' + feature_str)


# build targets
if win32
    windows = import('windows')
    res_flags = ['--codepage=65001']

    # Unintuitively, this compile operates out of the osdep subdirectory.
    # Hence, these includes are needed.
    res_includes = [source_root, build_root]

    resources = ['etc/mpv-icon-8bit-16x16.png',
                 'etc/mpv-icon-8bit-32x32.png',
                 'etc/mpv-icon-8bit-64x64.png',
                 'etc/mpv-icon-8bit-128x128.png',
                 'etc/mpv-icon.ico',
                 'osdep/mpv.exe.manifest']

    sources += windows.compile_resources('osdep/mpv.rc', args: res_flags, depend_files: resources,
                                         depends: version_h, include_directories: res_includes)
endif


if get_option('libmpv')
    client_h_define = cc.get_define('MPV_CLIENT_API_VERSION', prefix: '#include "libmpv/client.h"',
                                    include_directories: include_directories('.'))
    major = client_h_define.split('|')[0].split('<<')[0].strip('() ')
    minor = client_h_define.split('|')[1].strip('() ')
    client_api_version = major + '.' + minor + '.0'

    libmpv = library('mpv', sources, dependencies: dependencies, gnu_symbol_visibility: 'hidden',
                     version: client_api_version, include_directories: includedir, install: true)
    pkg = import('pkgconfig')
    pkg.generate(libmpv, version: client_api_version,
                 description: 'mpv media player client library')

    headers = ['libmpv/client.h', 'libmpv/render.h',
               'libmpv/render_gl.h', 'libmpv/stream_cb.h']
    install_headers(headers, subdir: 'mpv')
endif

if get_option('cplayer')
    datadir = get_option('datadir')
    confdir = get_option('sysconfdir')

    conf_files = ['etc/mpv.conf', 'etc/input.conf',
                  'etc/mplayer-input.conf', 'etc/restore-old-bindings.conf']
    install_data(conf_files, install_dir: join_paths(datadir, 'doc', 'mpv'))

    bash_install_dir = join_paths(datadir, 'bash-completion', 'completions')
    install_data('etc/mpv.bash-completion', install_dir: bash_install_dir, rename: 'mpv')

    zsh_install_dir = join_paths(datadir, 'zsh', 'site-functions')
    install_data('etc/_mpv.zsh', install_dir: zsh_install_dir, rename: '_mpv')

    install_data('etc/mpv.desktop', install_dir: join_paths(datadir, 'applications'))
    install_data('etc/mpv.metainfo.xml', install_dir: join_paths(datadir, 'metainfo'))
    install_data('etc/encoding-profiles.conf', install_dir: join_paths(confdir, 'mpv'))

    foreach size: ['16x16', '32x32', '64x64', '128x128']
        icon_dir = join_paths(datadir, 'icons', 'hicolor', size, 'apps')
        install_data('etc/mpv-icon-8bit-' + size + '.png', install_dir: icon_dir, rename: 'mpv.png')
    endforeach

    hicolor_dir = join_paths(datadir, 'icons', 'hicolor')
    install_data('etc/mpv-gradient.svg', install_dir: join_paths(hicolor_dir, 'scalable', 'apps'),
                 rename: 'mpv.svg')
    install_data('etc/mpv-symbolic.svg', install_dir: join_paths(hicolor_dir, 'symbolic', 'apps'))

    executable('mpv', sources, dependencies: dependencies, win_subsystem: 'windows,6.0',
               include_directories: includedir, install: true)
endif

summary({'libmpv': get_option('libmpv'),
         'lua': features['lua']},
         bool_yn: true)
