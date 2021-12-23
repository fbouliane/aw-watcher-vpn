import argparse

from aw_core.log import setup_logging

from aw_watcher_openvpn.watch import OpenvpnWatcher


def main() -> None:
    # Set up argparse
    parser = argparse.ArgumentParser("A watcher for keyboard and mouse input to detect AFK state")
    parser.add_argument("-v", "--verbose", dest='verbose', action="store_true",
                        help='run with verbose logging')
    parser.add_argument("--testing", action="store_true",
                        help='run in testing mode')

    args = parser.parse_args()

    # Set up logging
    setup_logging("aw-watcher-openvpn",
                  testing=args.testing, verbose=args.verbose,
                  log_stderr=True, log_file=True)

    # Start watcher
    watcher = OpenvpnWatcher(testing=args.testing)
    watcher.run()


if __name__ == "__main__":
    main()
