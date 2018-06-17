import os, sys
import argparse
import logging, time
import datetime
from watchdog import events
from watchdog.observers import Observer
import codecs


start_keyword = '[INFO]OkToPuSz adminszolgálatba lépett.'
end_keyword = '[INFO]OkToPuSz kilépett az adminszolgálatból.'

opened_keyword = False
changed_keyword = False

start_time = None


class ChangeEvent(events.PatternMatchingEventHandler):
    def on_modified(self, event):
        super(ChangeEvent, self).on_modified(event)
        check_log_time()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Monitor a file for changes and log them.',
        epilog='With love from Kvazhir <3',
        add_help=False
    )

    opt_arg = parser.add_argument_group('optional arguments')
    opt_arg.add_argument('-h', '--help', action='help', help='show this help message and exit')
    opt_arg.add_argument('-v', '--verbose', action='store_true', help='enable verbosity')
    opt_arg.add_argument('-ks', '--keyword_start', 
        action='store', 
        help='the keyword for starting the timer (default: [INFO]OkToPuSz adminszolgálatba lépett.)',
        default='[INFO]OkToPuSz adminszolgálatba lépett.'
    )
    opt_arg.add_argument('-ke', '--keyword_end', 
        action='store', 
        help='the keyword for ending the timer (default: [INFO]OkToPuSz kilépett az adminszolgálatból.)',
        default='[INFO]OkToPuSz kilépett az adminszolgálatból.'
    )
    opt_arg.add_argument('--version', action='version', version='%(prog)s 0.1')


    req_arg = parser.add_argument_group('required arguments')
    req_arg.add_argument('-i', '--input', 
        action='store', 
        help='path to input file',
        metavar='<input_path>',
        required=True
    )
    req_arg.add_argument('-o', '--output',
        action='store',
        help='path to log output',
        metavar='<output_path>',
        required=True
    )

    args = parser.parse_args()

    args.input = os.path.abspath(args.input)

    return args


def check_log_time():
    global opened_keyword
    global start_keyword
    global end_keyword
    global start_time
    global changed_keyword

    content = read_file.read()

    content.encode('utf-8')
    
    if args.verbose:
        print(content)

    logging.debug(content)

    if not opened_keyword:
        if start_keyword in content:
            start_time = datetime.datetime.now()

            if args.verbose:
                if not changed_keyword:
                    print('OkToPuSz came ONLINE.')
                else:
                    print('Timer started.')

            logging.debug('in %s', str(start_time))
            log_file.write('IN: ' + str(start_time) + '\n')
            opened_keyword = True
    else:
        if end_keyword in content:
            end_time = datetime.datetime.now()

            if args.verbose:
                if not changed_keyword:
                    print('OkToPuSz went OFFLINE.')
                else:
                    print('Timer stopped and logged.')
                
            logging.debug('out %s', str(end_time))
            log_file.write('OUT: ' + str(end_time) + '\n')

            log_file.write('SESSION: ' + str(end_time - start_time) + '\n\n')
            opened_keyword = False

    log_file.flush()
    os.fsync(log_file.fileno())


def main():
    global args
    global read_file
    global log_file
    global start_keyword
    global end_keyword
    global changed_keyword

    args = parse_arguments()

    if os.path.isfile('log_timer_debug.log'):
        if os.stat('log_timer_debug.log').st_size > 1000000000: # 1gb
            os.remove('log_timer_debug.log')

    if args.keyword_start != start_keyword:
        start_keyword = args.keyword_start
        changed_keyword = True

    if args.keyword_end != end_keyword:
        end_keyword = args.keyword_end
        changed_keyword = True

    if args.verbose:
        print('Starting keyword:', start_keyword)
        print('Ending keyword:', end_keyword)

    logging.basicConfig(filename='log_timer_debug.log',
                        filemode='a',
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    event_handler = ChangeEvent([args.input])
    observer = Observer()

    observer.schedule(event_handler, os.path.dirname(args.input), recursive=False)

    try:
        read_file = codecs.open(args.input, encoding='utf-8', mode='r')
        log_file = codecs.open(args.output, encoding='utf-8', mode='a')

        read_file.seek(0, 2)

    except OSError as e:
        logging.error(str(e))
        sys.exit(1)


    try:
        observer.start()

    except FileNotFoundError as e:
        logging.error(str(e))
        sys.exit(1)

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        read_file.close()
        log_file.close()
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
    sys.exit(0)
