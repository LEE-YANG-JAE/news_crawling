import run_headline_crawling
import run_economics_crawling
import run_opinions_crawling


def main():
    print("Starting combined execution...")

    # Run headline crawling
    run_headline_crawling.main()

    # Run headline crawling
    run_economics_crawling.main()

    # Run opinions crawling
    run_opinions_crawling.main()

    print("Finished combined execution.")


if __name__ == "__main__":
    main()