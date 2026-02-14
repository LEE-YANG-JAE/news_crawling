import run_headline_crawling
import run_economics_crawling
import run_opinions_crawling
import run_eng_stock_check


def main():
    print("Starting combined execution...")

    # Run headline crawling
    run_headline_crawling.main()

    # Run headline crawling
    run_economics_crawling.main()

    # Run opinions crawling
    run_opinions_crawling.main()

    # Run eng stock news crawling
    run_eng_stock_check.main()

    print("Finished combined execution.")


if __name__ == "__main__":
    main()
