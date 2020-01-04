import os
import random
import gzip
import argparse


def create_smaller_log(fn_from, fn_to, n):
    """Sample smaller log from a larger one.

    Function samples n records from .gz log and
    save it to the output .gz file.

    Args:
        fn_from (str): path to the log in .gz format to sample from.
        fn_to (str): out path in .gz format.
        n (int): number of reconds to sample to out log.
    """
    lines = []
    with gzip.open(fn_from, 'rb') as f:
        for i, line in enumerate(f.readlines()[:n]):
            lines.append(line)
    with gzip.open(fn_to, 'wb') as f:
        f.writelines(lines)


def generate_logs(fn_from, dest_dir, n_logs=10):
    """Create multiple logs sample from some file.

    Args:
        fn_from (str): log .gz file to sample from.
         ource_dir (str): directory to put logs to.
        n_logs (int): number of logs to generate.
    """
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    with gzip.open(fn_from, 'rb') as f:
        lines = f.readlines()

    # Convert binary object to strings
    lines = list(map(lambda x: x.decode('utf-8'), lines))

    for _ in range(n_logs):
        n = random.randrange(100, len(lines))
        inds = [random.randrange(len(lines)) for _ in range(n)]
        lines_samples = [lines[i] for i in inds]

        ry = random.randint(2000, 2020)
        rm = random.randint(1, 12)
        rd = random.randint(1, 29)
        gz_format = random.randrange(2)

        if gz_format:
            fn = f"nginx-access.log-{ry}{rm:02d}{rd:02d}.gz"
            with gzip.open(os.path.join(dest_dir, fn), 'wb') as f:
                for line in lines_samples:
                    f.write(line.encode())
        else:
            fn = f"nginx-access.log-{ry}{rm:02d}{rd:02d}.log"
            with open(os.path.join(dest_dir, fn), 'w') as f:
                f.writelines(lines_samples)


if __name__ == "__main__":
    # create_smaller_log(fn_from="nginx-access-ui.log-20170630.gz",
    #                   fn_to="log-10k-20190102.gz",
    #                    n=10_000)

    parser = argparse.ArgumentParser(description="Default logs generation.")
    parser.add_argument("--source_log", type=str, help="Source .gz log")
    parser.add_argument("--dest_dir", type=str, default="log",
                        help="Directory for generated logs")
    parser.add_argument("--n", type=int, default=10, help="Number of logs")
    args = parser.parse_args()

    generate_logs(args.source_log, args.dest_dir, args.n)
