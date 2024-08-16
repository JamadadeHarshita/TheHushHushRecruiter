import requests
import time

# Base URL for Stack Exchange API
base_url = "https://api.stackexchange.com/2.3"
    

# Function to make a request with exponential backoff
def fetch_with_backoff(url, max_retries=5):
    retries = 0
    while retries < max_retries:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:  # Too Many Requests
            # Get the retry-after time from the headers if available
            retry_after = response.headers.get('X-RateLimit-Reset', 1)
            wait_time = int(retry_after)
            print(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
            time.sleep(wait_time)
        else:
            print(f"Request failed with status code {response.status_code}.")
            response.raise_for_status()
        retries += 1
        wait_time = 2 ** retries  # Exponential backoff
        time.sleep(wait_time)
    raise Exception("Max retries exceeded")

# Function to fetch user data with additional details
def fetch_user_data(user_ids):
    user_data = []
    for user_id in user_ids:
        user_response = requests.get(f"{base_url}/users/{user_id}?site=stackoverflow").json()
        if user_response.get('items'):
            user_info = user_response['items'][0]

            # top tags
            tags_response = requests.get(f"{base_url}/users/{user_id}/tags?site=stackoverflow&order=desc&sort=popular").json()
            top_tags = [tag['name'] for tag in tags_response.get('items', [])[:2]]  # Only top 2 tags

            # answers and count accepted and not accepted
            answers_response = requests.get(f"{base_url}/users/{user_id}/answers?site=stackoverflow").json()
            is_accepted_true_count = 0
            is_accepted_false_count = 0
            
            for answer in answers_response.get('items', []):
                is_accepted = answer.get('is_accepted', False)
                
                # Count the number of accepted and not accepted answers
                if is_accepted:
                    is_accepted_true_count += 1
                else:
                    is_accepted_false_count += 1

            # Aggregate data
            user_data.append({
                "user_id": user_info['user_id'],
                "user_name": user_info['display_name'],
                "reputation": user_info['reputation'],
                "top_tags": top_tags,
                "accepted_count": is_accepted_true_count,
                "not_accepted_count": is_accepted_false_count,
            })
    return user_data

user_ids = [335858, 15168, 23283]
users = fetch_user_data(user_ids)
for user in users:
    print(user)

    
    
