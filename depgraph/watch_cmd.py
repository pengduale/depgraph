"""CLI entry point for the --watch / live-reload mode."""

import argparse
import sys
from typing import Optional

from depgraph.watcher import watch
from depgraph.rebuild import rebuild


def _make_callback(
    paths: list[str],
    output_svg: Optional[str],
    export_format: Optional[str],
    export_path: Optional[str],
    verbose: bool,
):
    def _cb(added, modified, removed):
        changed = added + modified + removed
        if verbose:
            print(f"[watch] Changes detected: {changed}")
        rebuild(
            paths,
            output_svg=output_svg,
            export_format=export_format,
            export_path=export_path,
            verbose=verbose,
        )

    return _cb


def parse_watch_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="depgraph-watch",
        description="Watch source files and rebuild the dependency graph on changes.",
    )
    parser.add_argument("paths", nargs="+", help="Files or directories to watch")
    parser.add_argument("--output", default=None, help="SVG output file")
    parser.add_argument("--export-format", choices=["json", "dot"], default=None)
    parser.add_argument("--export-path", default=None)
    parser.add_argument("--interval", type=float, default=1.0, help="Poll interval (s)")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_watch_args(argv)
    if args.verbose:
        print(f"[watch] Watching {args.paths} (interval={args.interval}s)")

    # Perform an initial build immediately
    rebuild(
        args.paths,
        output_svg=args.output,
        export_format=args.export_format,
        export_path=args.export_path,
        verbose=args.verbose,
    )

    cb = _make_callback(
        args.paths,
        output_svg=args.output,
        export_format=args.export_format,
        export_path=args.export_path,
        verbose=args.verbose,
    )
    watch(args.paths, cb, interval=args.interval)


if __name__ == "__main__":
    main()
