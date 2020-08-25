from config import Config
import command_args
import steam_reporter

def main():

    args = command_args.parse_args()
    config = Config(args.config)

    steam_reporter.update_database(args, config)

if __name__ == '__main__':
    main()