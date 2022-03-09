import requests

def get_base_readme():

    file = open("./BASE.md", "r")
    data = str(file.read())
    file.close()

    return data

def main():

    data = get_data()

    # Sort by karma.
    data.sort(reverse=True)
    print(data)
    

    markdown = "![Wordcloud](./cloud.png)\n\n# Top 10 posts of r/DevOps in the last day\n\n| Title | Author | Score |\n|:---|:---|:---|\n"

    # Take the top 10 posts.
    for item in data[:10]:
        markdown += f"| [{item[1]}]({item[3]}) | {item[2]} | {item[0]} |\n"

    base_readme = get_base_readme()

    markdown = base_readme + "<br />" + markdown

    open("./README.md", "w", encoding="utf-8").write(markdown)


def get_data():

    submission_data = list()

    headers = {"User-Agent": "DevOps checker"}
    url = "https://www.reddit.com/r/devops/top.json?sort=top&t=day"

    with requests.get(url, headers=headers) as response:

        submissions = response.json()["data"]["children"]

        for item in submissions:
            title = item["data"]["title"]
            author = item["data"]["author"]
            score = item["data"]["score"]
            permalink = "https://www.reddit.com" + item["data"]["permalink"]

            submission_data.append([score, title, author, permalink])

    return submission_data


if __name__ == "__main__":

    main()
