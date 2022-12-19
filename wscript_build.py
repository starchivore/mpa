import re
import os

def _all_includes(ctx):
    return [ctx.bldnode.abspath(), ctx.srcnode.abspath()] + \
            ctx.dependencies_includes()

def build(ctx):
    ctx.load('waf_customizations')
    ctx.load('generators.sources')

    ctx(
        features = "file2string",
        source = "TOOLS/osxbundle/mpv.app/Contents/Resources/icon.icns",
        target = "generated/TOOLS/osxbundle/mpv.app/Contents/Resources/icon.icns.inc",
    )

    icons = [16, 32, 64, 128]
    for size in icons:
        name = "etc/mpv-icon-8bit-%dx%d.png" % (size, size)
        ctx(
            features = "file2string",
            source = name,
            target = "generated/%s.inc" % name,
        )

    ctx(
        features = "file2string",
        source = "etc/input.conf",
        target = "generated/etc/input.conf.inc",
    )

    ctx(
        features = "file2string",
        source = "etc/builtin.conf",
        target = "generated/etc/builtin.conf.inc",
    )

    ctx(
        features = "file2string",
        source = "sub/osd_font.otf",
        target = "generated/sub/osd_font.otf.inc",
    )

    lua_files = ["defaults.lua", "assdraw.lua", "options.lua", "osc.lua",
                 "ytdl_hook.lua", "stats.lua", "console.lua",
                 "auto_profiles.lua"]

    for fn in lua_files:
        fn = "player/lua/" + fn
        ctx(
            features = "file2string",
            source = fn,
            target = "generated/%s.inc" % fn,
        )

    ctx(
        features = "file2string",
        source = "player/javascript/defaults.js",
        target = "generated/player/javascript/defaults.js.inc",
    )

    if ctx.dependency_satisfied('wayland'):
        ctx.wayland_protocol_code(proto_dir = ctx.env.WL_PROTO_DIR,
            protocol  = "stable/xdg-shell/xdg-shell",
            target    = "generated/wayland/xdg-shell.c")
        ctx.wayland_protocol_header(proto_dir = ctx.env.WL_PROTO_DIR,
            protocol  = "stable/xdg-shell/xdg-shell",
            target    = "generated/wayland/xdg-shell.h")
        ctx.wayland_protocol_code(proto_dir = ctx.env.WL_PROTO_DIR,
            protocol  = "unstable/idle-inhibit/idle-inhibit-unstable-v1",
            target    = "generated/wayland/idle-inhibit-unstable-v1.c")
        ctx.wayland_protocol_header(proto_dir = ctx.env.WL_PROTO_DIR,
            protocol  = "unstable/idle-inhibit/idle-inhibit-unstable-v1",
            target    = "generated/wayland/idle-inhibit-unstable-v1.h")
        ctx.wayland_protocol_code(proto_dir = ctx.env.WL_PROTO_DIR,
            protocol  = "stable/presentation-time/presentation-time",
            target    = "generated/wayland/presentation-time.c")
        ctx.wayland_protocol_header(proto_dir = ctx.env.WL_PROTO_DIR,
            protocol  = "stable/presentation-time/presentation-time",
            target    = "generated/wayland/presentation-time.h")
        ctx.wayland_protocol_code(proto_dir = ctx.env.WL_PROTO_DIR,
            protocol  = "unstable/xdg-decoration/xdg-decoration-unstable-v1",
            target    = "generated/wayland/xdg-decoration-unstable-v1.c")
        ctx.wayland_protocol_header(proto_dir = ctx.env.WL_PROTO_DIR,
            protocol  = "unstable/xdg-decoration/xdg-decoration-unstable-v1",
            target    = "generated/wayland/xdg-decoration-unstable-v1.h")
        ctx.wayland_protocol_code(proto_dir = ctx.env.WL_PROTO_DIR,
            protocol  = "unstable/linux-dmabuf/linux-dmabuf-unstable-v1",
            target    = "generated/wayland/linux-dmabuf-unstable-v1.c")
        ctx.wayland_protocol_header(proto_dir = ctx.env.WL_PROTO_DIR,
            protocol  = "unstable/linux-dmabuf/linux-dmabuf-unstable-v1",
            target    = "generated/wayland/linux-dmabuf-unstable-v1.h")
        ctx.wayland_protocol_code(proto_dir = ctx.env.WL_PROTO_DIR,
            protocol  = "stable/viewporter/viewporter",
            target    = "generated/wayland/viewporter.c")
        ctx.wayland_protocol_header(proto_dir = ctx.env.WL_PROTO_DIR,
            protocol  = "stable/viewporter/viewporter",
            target    = "generated/wayland/viewporter.h")

    if ctx.dependency_satisfied('wayland-protocols-1-27'):
        ctx.wayland_protocol_code(proto_dir = ctx.env.WL_PROTO_DIR,
            protocol  = "staging/content-type/content-type-v1",
            target    = "generated/wayland/content-type-v1.c")
        ctx.wayland_protocol_header(proto_dir = ctx.env.WL_PROTO_DIR,
            protocol  = "staging/content-type/content-type-v1",
            target    = "generated/wayland/content-type-v1.h")
        ctx.wayland_protocol_code(proto_dir = ctx.env.WL_PROTO_DIR,
            protocol  = "staging/single-pixel-buffer/single-pixel-buffer-v1",
            target    = "generated/wayland/single-pixel-buffer-v1.c")
        ctx.wayland_protocol_header(proto_dir = ctx.env.WL_PROTO_DIR,
            protocol  = "staging/single-pixel-buffer/single-pixel-buffer-v1",
            target    = "generated/wayland/single-pixel-buffer-v1.h")

    ctx(features = "ebml_header", target = "generated/ebml_types.h")
    ctx(features = "ebml_definitions", target = "generated/ebml_defs.inc")

    def swift(task):
        src = [x.abspath() for x in task.inputs]
        bridge = ctx.path.find_node("osdep/macOS_swift_bridge.h").abspath()
        tgt = task.outputs[0].abspath()
        header = task.outputs[1].abspath()
        module = task.outputs[2].abspath()
        module_name = os.path.basename(module).rsplit(".", 1)[0]

        cmd = [ ctx.env.SWIFT ]
        cmd.extend(ctx.env.SWIFT_FLAGS)
        cmd.extend([
            "-module-name", module_name,
            "-emit-module-path", module,
            "-import-objc-header", bridge,
            "-emit-objc-header-path", header,
            "-o", tgt,
        ])
        cmd.extend(src)
        cmd.extend([ "-I.", "-I%s" % ctx.srcnode.abspath() ])

        return task.exec_command(cmd)

    if ctx.dependency_satisfied('cocoa') and ctx.dependency_satisfied('swift'):
        swift_source = [
            ( "osdep/macos/log_helper.swift" ),
            ( "osdep/macos/libmpv_helper.swift" ),
            ( "osdep/macos/mpv_helper.swift" ),
            ( "osdep/macos/swift_extensions.swift" ),
            ( "osdep/macos/swift_compat.swift" ),
            ( "osdep/macos/remote_command_center.swift", "macos-media-player" ),
            ( "video/out/mac/common.swift" ),
            ( "video/out/mac/view.swift" ),
            ( "video/out/mac/window.swift" ),
            ( "video/out/mac/title_bar.swift" ),
            ( "video/out/cocoa_cb_common.swift", "macos-cocoa-cb" ),
            ( "video/out/mac/gl_layer.swift", "macos-cocoa-cb" ),
        ]

        ctx(
            rule   = swift,
            source = ctx.filtered_sources(swift_source),
            target = [ "osdep/macOS_swift.o",
                       "osdep/macOS_swift.h",
                       "osdep/macOS_swift.swiftmodule" ],
            before = 'c',
        )

        ctx.env.append_value('LINKFLAGS', [
            '-Xlinker', '-add_ast_path',
            '-Xlinker', ctx.path.find_or_declare("osdep/macOS_swift.swiftmodule").abspath()
        ])

    if ctx.dependency_satisfied('cplayer'):
        main_fn_c = ctx.pick_first_matching_dep([
            ( "osdep/main-fn-cocoa.c",               "cocoa" ),
            ( "osdep/main-fn-unix.c",                "posix" ),
            ( "osdep/main-fn-win.c",                 "win32-desktop" ),
        ])

    getch2_c = ctx.pick_first_matching_dep([
        ( "osdep/terminal-unix.c",               "posix" ),
        ( "osdep/terminal-win.c",                "win32-desktop" ),
        ( "osdep/terminal-dummy.c" ),
    ])

    timer_c = ctx.pick_first_matching_dep([
        ( "osdep/timer-win2.c",                  "os-win32" ),
        ( "osdep/timer-darwin.c",                "os-darwin" ),
        ( "osdep/timer-linux.c",                 "posix" ),
    ])

    ipc_c = ctx.pick_first_matching_dep([
        ( "input/ipc-unix.c",                    "posix" ),
        ( "input/ipc-win.c",                     "win32-desktop" ),
        ( "input/ipc-dummy.c" ),
    ])

    subprocess_c = ctx.pick_first_matching_dep([
        ( "osdep/subprocess-posix.c",            "posix" ),
        ( "osdep/subprocess-win.c",              "win32-desktop" ),
        ( "osdep/subprocess-dummy.c" ),
    ])

    sources = [
        ## Audio
        ( "audio/aframe.c" ),
        ( "audio/chmap.c" ),
        ( "audio/chmap_avchannel.c", "av-channel-layout" ),
        ( "audio/chmap_sel.c" ),
        ( "audio/decode/ad_lavc.c" ),
        ( "audio/decode/ad_spdif.c" ),
        ( "audio/filter/af_drop.c" ),
        ( "audio/filter/af_format.c" ),
        ( "audio/filter/af_lavcac3enc.c" ),
        ( "audio/filter/af_rubberband.c",        "rubberband" ),
        ( "audio/filter/af_scaletempo.c" ),
        ( "audio/filter/af_scaletempo2.c" ),
        ( "audio/filter/af_scaletempo2_internals.c" ),
        ( "audio/fmt-conversion.c" ),
        ( "audio/format.c" ),
        ( "audio/out/ao.c" ),
        ( "audio/out/ao_lavc.c" ),
        ( "audio/out/ao_null.c" ),
        ( "audio/out/ao_pcm.c" ),
        ( "audio/out/ao_wasapi.c",               "wasapi" ),
        ( "audio/out/ao_wasapi_changenotify.c",  "wasapi" ),
        ( "audio/out/ao_wasapi_utils.c",         "wasapi" ),
        ( "audio/out/buffer.c" ),

        ## Core
        ( "common/av_common.c" ),
        ( "common/av_log.c" ),
        ( "common/codecs.c" ),
        ( "common/common.c" ),
        ( "common/encode_lavc.c" ),
        ( "common/msg.c" ),
        ( "common/playlist.c" ),
        ( "common/recorder.c" ),
        ( "common/stats.c" ),
        ( "common/tags.c" ),
        ( "common/version.c" ),

        ## Demuxers
        ( "demux/codec_tags.c" ),
        ( "demux/cue.c" ),
        ( "demux/cache.c" ),
        ( "demux/demux.c" ),
        ( "demux/demux_cue.c" ),
        ( "demux/demux_disc.c" ),
        ( "demux/demux_edl.c" ),
        ( "demux/demux_lavf.c" ),
        ( "demux/demux_libarchive.c",            "libarchive" ),
        ( "demux/demux_mf.c" ),
        ( "demux/demux_mkv.c" ),
        ( "demux/demux_mkv_timeline.c" ),
        ( "demux/demux_null.c" ),
        ( "demux/demux_playlist.c" ),
        ( "demux/demux_raw.c" ),
        ( "demux/demux_timeline.c" ),
        ( "demux/ebml.c" ),
        ( "demux/packet.c" ),
        ( "demux/timeline.c" ),

        ( "filters/f_async_queue.c" ),
        ( "filters/f_autoconvert.c" ),
        ( "filters/f_auto_filters.c" ),
        ( "filters/f_decoder_wrapper.c" ),
        ( "filters/f_demux_in.c" ),
        ( "filters/f_hwtransfer.c" ),
        ( "filters/f_lavfi.c" ),
        ( "filters/f_output_chain.c" ),
        ( "filters/f_swresample.c" ),
        ( "filters/f_swscale.c" ),
        ( "filters/f_utils.c" ),
        ( "filters/filter.c" ),
        ( "filters/frame.c" ),
        ( "filters/user_filters.c" ),

        ## Input
        ( "input/cmd.c" ),
        ( "input/event.c" ),
        ( "input/input.c" ),
        ( "input/ipc.c" ),
        ( ipc_c ),
        ( "input/keycodes.c" ),
        ( "input/sdl_gamepad.c",                 "sdl2-gamepad" ),

        ## Misc
        ( "misc/bstr.c" ),
        ( "misc/charset_conv.c" ),
        ( "misc/dispatch.c" ),
        ( "misc/jni.c",                          "android" ),
        ( "misc/json.c" ),
        ( "misc/natural_sort.c" ),
        ( "misc/node.c" ),
        ( "misc/rendezvous.c" ),
        ( "misc/random.c" ),
        ( "misc/thread_pool.c" ),
        ( "misc/thread_tools.c" ),

        ## Options
        ( "options/m_config_core.c" ),
        ( "options/m_config_frontend.c" ),
        ( "options/m_option.c" ),
        ( "options/m_property.c" ),
        ( "options/options.c" ),
        ( "options/parse_commandline.c" ),
        ( "options/parse_configfile.c" ),
        ( "options/path.c" ),

        ## Player
        ( "player/audio.c" ),
        ( "player/client.c" ),
        ( "player/command.c" ),
        ( "player/configfiles.c" ),
        ( "player/external_files.c" ),
        ( "player/javascript.c",                 "javascript" ),
        ( "player/loadfile.c" ),
        ( "player/lua.c",                        "lua" ),
        ( "player/main.c" ),
        ( "player/misc.c" ),
        ( "player/osd.c" ),
        ( "player/playloop.c" ),
        ( "player/screenshot.c" ),
        ( "player/scripting.c" ),
        ( "player/sub.c" ),
        ( "player/video.c" ),

        ## Streams
        ( "stream/cookies.c" ),
        ( "stream/dvb_tune.c",                   "dvbin" ),
        ( "stream/stream.c" ),
        ( "stream/stream_avdevice.c" ),
        ( "stream/stream_bluray.c",              "libbluray" ),
        ( "stream/stream_cb.c" ),
        ( "stream/stream_cdda.c",                "cdda" ),
        ( "stream/stream_concat.c" ),
        ( "stream/stream_slice.c" ),
        ( "stream/stream_dvb.c",                 "dvbin" ),
        ( "stream/stream_dvdnav.c",              "dvdnav" ),
        ( "stream/stream_edl.c" ),
        ( "stream/stream_file.c" ),
        ( "stream/stream_lavf.c" ),
        ( "stream/stream_libarchive.c",          "libarchive" ),
        ( "stream/stream_memory.c" ),
        ( "stream/stream_mf.c" ),
        ( "stream/stream_null.c" ),

        ## Subtitles
        ( "sub/ass_mp.c" ),
        ( "sub/dec_sub.c" ),
        ( "sub/draw_bmp.c" ),
        ( "sub/filter_regex.c",                  "posix" ),
        ( "sub/filter_jsre.c",                   "javascript" ),
        ( "sub/filter_sdh.c" ),
        ( "sub/img_convert.c" ),
        ( "sub/lavc_conv.c" ),
        ( "sub/osd.c" ),
        ( "sub/osd_libass.c" ),
        ( "sub/sd_ass.c" ),
        ( "sub/sd_lavc.c" ),

        ## Tests
        ( "test/chmap.c",                        "tests" ),
        ( "test/gl_video.c",                     "tests" ),
        ( "test/img_format.c",                   "tests" ),
        ( "test/json.c",                         "tests" ),
        ( "test/linked_list.c",                  "tests" ),
        ( "test/paths.c",                        "tests" ),
        ( "test/repack.c",                       "tests && zimg" ),
        ( "test/scale_sws.c",                    "tests" ),
        ( "test/scale_test.c",                   "tests" ),
        ( "test/scale_zimg.c",                   "tests && zimg" ),
        ( "test/tests.c",                        "tests" ),

        ## osdep
        ( getch2_c ),
        ( "osdep/io.c" ),
        ( "osdep/threads.c" ),
        ( "osdep/timer.c" ),
        ( timer_c ),
        ( "osdep/polldev.c",                     "posix" ),

        ( "osdep/android/strnlen.c",             "android"),
        ( "osdep/glob-win.c",                    "glob-win32" ),
        ( "osdep/macosx_application.m",          "cocoa" ),
        ( "osdep/macosx_events.m",               "cocoa" ),
        ( "osdep/macosx_menubar.m",              "cocoa" ),
        ( "osdep/macosx_touchbar.m",             "macos-touchbar" ),
        ( "osdep/mpv.rc",                        "win32-executable" ),
        ( "osdep/path-macosx.m",                 "cocoa" ),
        ( "osdep/path-unix.c"),
        ( "osdep/path-uwp.c",                    "uwp" ),
        ( "osdep/path-win.c",                    "win32-desktop" ),
        ( "osdep/semaphore_osx.c" ),
        ( "osdep/subprocess.c" ),
        ( subprocess_c ),
        ( "osdep/w32_keyboard.c",                "os-cygwin" ),
        ( "osdep/w32_keyboard.c",                "os-win32" ),
        ( "osdep/win32/pthread.c",               "win32-internal-pthreads"),
        ( "osdep/windows_utils.c",               "os-cygwin" ),
        ( "osdep/windows_utils.c",               "os-win32" ),

        ## tree_allocator
        "ta/ta.c", "ta/ta_talloc.c", "ta/ta_utils.c"
    ]

    if ctx.dependency_satisfied('win32-executable'):
        from waflib import TaskGen

        TaskGen.declare_chain(
            name    = 'windres',
            rule    = '${WINDRES} ${WINDRES_FLAGS} ${SRC} ${TGT}',
            ext_in  = '.rc',
            ext_out = '-rc.o',
            color   = 'PINK')

        ctx.env.WINDRES_FLAGS = [
            '--include-dir={0}'.format(ctx.bldnode.abspath()),
            '--include-dir={0}'.format(ctx.srcnode.abspath()),
            '--codepage=65001' # Unicode codepage
        ]

        for node in 'osdep/mpv.exe.manifest etc/mpv-icon.ico'.split():
            ctx.add_manual_dependency(
                ctx.path.find_node('osdep/mpv.rc'),
                ctx.path.find_node(node))

        version = ctx.bldnode.find_node('generated/version.h')
        if version:
            ctx.add_manual_dependency(
                ctx.path.find_node('osdep/mpv.rc'),
                version)

    if ctx.dependency_satisfied('cplayer'):
        ctx(
            target       = "objects",
            source       = ctx.filtered_sources(sources),
            use          = ctx.dependencies_use(),
            includes     = _all_includes(ctx),
            features     = "c",
        )

    syms = False
    if ctx.dependency_satisfied('cplugins'):
        syms = True
        ctx.load("syms")

    additional_objects = []
    if ctx.dependency_satisfied('swift'):
        additional_objects.append("osdep/macOS_swift.o")

    if ctx.dependency_satisfied('cplayer'):
        ctx(
            target       = "mpv",
            source       = main_fn_c,
            use          = ctx.dependencies_use() + ['objects'],
            add_objects  = additional_objects,
            includes     = _all_includes(ctx),
            features     = "c cprogram" + (" syms" if syms else ""),
            export_symbols_def = "libmpv/mpv.def", # for syms=True
            install_path = ctx.env.BINDIR
        )
        for f in ['mpv.conf', 'input.conf', 'mplayer-input.conf', \
                  'restore-old-bindings.conf']:
            ctx.install_as(os.path.join(ctx.env.DOCDIR, f),
                           os.path.join('etc/', f))

        if ctx.env.DEST_OS == 'win32':
            wrapctx = ctx(
                target       = "mpv",
                source       = ['osdep/win32-console-wrapper.c'],
                features     = "c cprogram",
                install_path = ctx.env.BINDIR
            )

            wrapctx.env.cprogram_PATTERN = "%s.com"
            wrapflags = ['-municode', '-Wl,--subsystem,console']
            wrapctx.env.CFLAGS = ctx.env.CFLAGS + wrapflags
            wrapctx.env.LAST_LINKFLAGS = ctx.env.LAST_LINKFLAGS + wrapflags

    build_shared = ctx.dependency_satisfied('libmpv-shared')
    build_static = ctx.dependency_satisfied('libmpv-static')
    if build_shared or build_static:
        if build_shared:
            waftoolsdir = os.path.join(os.path.dirname(__file__), "waftools")
            ctx.load("syms", tooldir=waftoolsdir)
        vre = '#define MPV_CLIENT_API_VERSION MPV_MAKE_VERSION\((.*), (.*)\)'
        libmpv_header = ctx.path.find_node("libmpv/client.h").read()
        major, minor = re.search(vre, libmpv_header).groups()
        libversion = major + '.' + minor + '.0'

        def _build_libmpv(shared):
            features = "c "
            if shared:
                features += "cshlib syms"
            else:
                features += "cstlib"

            libmpv_kwargs = {
                "target": "mpv",
                "source":   ctx.filtered_sources(sources),
                "use":      ctx.dependencies_use(),
                "add_objects": additional_objects,
                "includes": [ctx.bldnode.abspath(), ctx.srcnode.abspath()] + \
                             ctx.dependencies_includes(),
                "features": features,
                "export_symbols_def": "libmpv/mpv.def",
                "install_path": ctx.env.LIBDIR,
                "install_path_implib": ctx.env.LIBDIR,
            }

            if shared and ctx.dependency_satisfied('android'):
                # for Android we just add the linker flag without version
                # as we still need the SONAME for proper linkage.
                # (LINKFLAGS logic taken from waf's apply_vnum in ccroot.py)
                v=ctx.env.SONAME_ST%'libmpv.so'
                ctx.env.append_value('LINKFLAGS',v.split())
            else:
                # for all other configurations we want SONAME to be used
                libmpv_kwargs["vnum"] = libversion

            if shared and ctx.env.DEST_OS == 'win32':
                libmpv_kwargs["install_path"] = ctx.env.BINDIR

            ctx(**libmpv_kwargs)

        if build_shared:
            _build_libmpv(True)
        if build_static:
            _build_libmpv(False)

        def get_deps():
            res = []
            for k in ctx.env.keys():
                if (k.startswith("LIB_") and k != "LIB_ST") \
                or (k.startswith("STLIB_") and k != "STLIB_ST" and k != "STLIB_MARKER"):
                    for l in ctx.env[k]:
                        if l in res:
                            res.remove(l)
                        res.append(l)
            return " ".join(["-l" + l for l in res])

        ctx(
            target       = 'libmpv/mpv.pc',
            source       = 'libmpv/mpv.pc.in',
            features     = 'subst',
            PREFIX       = ctx.env.PREFIX,
            LIBDIR       = ctx.env.LIBDIR,
            INCDIR       = ctx.env.INCLUDEDIR,
            VERSION      = libversion,
            PRIV_LIBS    = get_deps(),
        )

        headers = ["client.h", "render.h",
                   "render_gl.h", "stream_cb.h"]
        for f in headers:
            ctx.install_as(ctx.env.INCLUDEDIR + '/mpv/' + f, 'libmpv/' + f)

        ctx.install_as(ctx.env.LIBDIR + '/pkgconfig/mpv.pc', 'libmpv/mpv.pc')

    if ctx.dependency_satisfied('html-build'):
        _build_html(ctx)

    if ctx.dependency_satisfied('manpage-build'):
        _build_man(ctx)

    if ctx.dependency_satisfied('pdf-build'):
        _build_pdf(ctx)

    if ctx.dependency_satisfied('cplayer'):

        if ctx.env.ZSHDIR:
            ctx.install_as(ctx.env.ZSHDIR + '/_mpv', 'etc/_mpv.zsh')

        if ctx.env.BASHDIR:
            ctx.install_as(ctx.env.BASHDIR + '/mpv', 'etc/mpv.bash-completion')

        ctx.install_files(
            ctx.env.DATADIR + '/applications',
            ['etc/mpv.desktop'] )

        ctx.install_files(
            ctx.env.DATADIR + '/metainfo',
            ['etc/mpv.metainfo.xml'] )

        ctx.install_files(ctx.env.CONFDIR, ['etc/encoding-profiles.conf'] )

        for size in '16x16 32x32 64x64 128x128'.split():
            ctx.install_as(
                ctx.env.DATADIR + '/icons/hicolor/' + size + '/apps/mpv.png',
                'etc/mpv-icon-8bit-' + size + '.png')

        ctx.install_as(
                ctx.env.DATADIR + '/icons/hicolor/scalable/apps/mpv.svg',
                'etc/mpv-gradient.svg')

        ctx.install_files(
            ctx.env.DATADIR + '/icons/hicolor/symbolic/apps',
            ['etc/mpv-symbolic.svg'])
