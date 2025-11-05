from apify_client import ApifyClient
import os
import pandas as pd
from dotenv import load_dotenv
import tqdm

load_dotenv()
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
ACTOR_ID = os.getenv("ACTOR_ID")

def scrape_linkedin_profiles(profiles_list, apify_token, actor_id):
    client = ApifyClient(apify_token)
    run = client.actor(actor_id).call(run_input={"startUrls": [{"url": p} for p in profiles_list]})
    dataset_id = run["defaultDatasetId"]
    return list(client.dataset(dataset_id).iterate_items())

if __name__ == "__main__":
    # load URLs from file
    with open(r"C:\Users\Aman\machine_learning_projects\LinkedIn Profile scrapper\Profile.txt", "r") as f:
        url = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(url)} URLs")

    results = scrape_linkedin_profiles(url)

    if results:
        df = pd.DataFrame(results)
        df.to_csv(r"C:\Users\Aman\machine_learning_projects\LinkedIn Profile scrapper\linkedin_profiles.csv", index=False)
        print("Saved linkedin_profiles.csv")
        print(df.head())   # show sample rows
    else:
        print("No data returned.")


