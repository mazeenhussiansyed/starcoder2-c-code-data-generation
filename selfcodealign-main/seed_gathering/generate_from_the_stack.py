import datasets
import os
import signal
from multiprocessing import Pool
from utils import process_chunk

def main(args):
    ds = datasets.load_dataset(
        args.dataset,
        args.data_dir,
        cache_dir=f"../nk569/stack",
        split="train",
        streaming="True",
    )
    i = 2000
    data_list = []
    for example in ds: 
        data_list.append(example)
        i -= 1
        if not i:
            break

    ds = data_list

    funs = set()
    total_len = len(ds)
    CHUNK_SIZE = 1000 * args.num_workers

    print(f"Total length: {total_len}")
    print(f"Chunk size: {CHUNK_SIZE}")

    chunk = []
    p = Pool(args.num_workers)
    for i, ex in enumerate(ds):
        if i % (total_len // 100) == 0:
            print(f"{i}/{total_len}")
        try:
            chunk.append(ex)
            if len(chunk) == CHUNK_SIZE or i == total_len - 1:
                print(f"Processing chunk {i // CHUNK_SIZE}")
                # divide the chunk into NUM_WORKERS chunks
                subchunk_size = len(chunk) // args.num_workers
                subchunks = [chunk[i:i + subchunk_size]
                             for i in range(0, len(chunk), subchunk_size)]
                new_funs_iter = p.imap(
                    process_chunk, [(i, subchunk) for i, subchunk in enumerate(subchunks)])
                print("Getting new functions")
                len_before = len(funs)
                while True:
                    try:
                        def timeout_handler(_, __):
                            raise KeyboardInterrupt  # it's fineeeeeee
                        signal.signal(signal.SIGALRM, timeout_handler)
                        signal.alarm(60)
                        funs.update(next(new_funs_iter))
                        signal.alarm(0)
                    except KeyboardInterrupt:
                        signal.alarm(0)
                        print("Keyboard interrupt. Terminating pool")
                        p.terminate()
                        p = Pool(args.num_workers)
                        break
                    except StopIteration:
                        break
                    except Exception as e:
                        print(e)

                signal.alarm(0)

                print(f"Done processing chunk {i // CHUNK_SIZE}. Got {len(funs) - len_before} new functions")

                chunk = []
        except Exception as e:
            print(e)
            chunk = []

        if i == total_len - 1:
            break

    p.close()

    new_ds_dict = {
        "content": list(funs),
        "id": list(range(len(funs)))
    }

    new_ds = datasets.Dataset.from_dict(new_ds_dict)
    new_ds.push_to_hub(args.push, private=True)
    print(new_ds)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_workers", type=int, default=os.cpu_count())
    parser.add_argument("--dataset", type=str,
                        default="bigcode/the-stack-v2-dedup")
    parser.add_argument("--data_dir", type=str, default="Python")
    parser.add_argument("--push", type=str, required=True)
    args = parser.parse_args()
    main(args)
