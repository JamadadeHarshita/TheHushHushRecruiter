import requests
import utilities
#from utilitiess.dataFetchUrls import urlsForDataFetch

def fetchstackoverRecords():
    api=utilities.urlsForDataFetch.get("stackoverflow")
    var=requests.get(api)
    #print(var)
    if var.status_code == 200:
        results=var.json()
        if "items" in results:
            for item in results["items"]:
                
                user_id = item.get('user_id')
                reputation = item.get('reputation')
                accept_rate = item.get('accept_rate')
                display_name = item.get('display_name')
                
                print(f"\nUser ID: {user_id}")
                print(f"Display Name: {display_name}")
                print(f"Reputation: {reputation}")
                print(f"Accept Rate: {accept_rate}%")
        
                if 'badge_counts' in item:
                    badge_counts= item['badge_counts']
                    print(badge_counts)
                    # print(f"Bronze: {badge_counts.get('bronze', 0)}")
                    # print(f"Silver: {badge_counts.get('silver', 0)}")
                    # print(f"Gold: {badge_counts.get('gold', 0)}")
                
                
                if "collectives" in item and len(item['collectives']) > 0:
                    tags = item['collectives'][0].get('collective', {}).get('tags', [])
                    print("\nTop 5 Tags for item:")
                    for tag in tags[:2]:
                        print(tag)
                        
        else:
            print("no items found in the results")
        
        # if "items" in results:
        #     for badge_counts in results['items']:
        #         print(badge_counts)
        #     for item in results["items"]:
        #         #print(badge_counts)
        #         if "collectives" in item:
        #             if len(item['collectives'])> 0:
        #                 tags=item['collectives'][0].get('collective',{}).get('tags',[])
        #                 for tag in tags[:5]:
        #                     print(tag)    
    else:
        print(f"Failed to retrieve data: {var.status_code}")
        
if __name__ == "__main__":
    fetchstackoverRecords()

