

import random
import csv
from datetime import datetime, timedelta

random.seed(42)

USERNAMES = [
    "@aisha_codes", "@rohan.tech", "@priya_designs", "@karan_vibes",
    "@dev_naina", "@thefoodie_raj", "@travel_with_meera", "@fit_arjun",
    "@musicby_sara", "@startup_vik", "@gamer_ananya", "@photo_kabir",
    "@bookworm_ira", "@chef_ishaan", "@artsy_diya",
]

HASHTAG_POOL = [
    "#python", "#ai", "#machinelearning", "#coding", "#tech",
    "#travel", "#foodie", "#fitness", "#motivation", "#music",
    "#startup", "#gaming", "#photography", "#books", "#art",
    "#datascience", "#webdev", "#opensource", "#productivity", "#news",
]

CATEGORIES = ["Technology", "Food", "Travel", "Fitness", "Entertainment",
              "Business", "Lifestyle", "Sports"]

CATEGORY_HASHTAGS = {
    "Technology": ["#python", "#ai", "#machinelearning", "#coding", "#tech",
                   "#datascience", "#webdev", "#opensource"],
    "Food": ["#foodie"],
    "Travel": ["#travel", "#photography"],
    "Fitness": ["#fitness", "#motivation"],
    "Entertainment": ["#music", "#gaming"],
    "Business": ["#startup", "#productivity", "#news"],
    "Lifestyle": ["#books", "#art", "#motivation"],
    "Sports": ["#fitness", "#motivation"],
}

POSITIVE_TEMPLATES = [
    "Absolutely loving the new {topic} update, this is amazing! {tags}",
    "Best {topic} experience ever, highly recommend it to everyone! {tags}",
    "So excited to share this incredible {topic} milestone with you all {tags}",
    "This {topic} community is so supportive and inspiring {tags}",
    "Grateful for such a wonderful {topic} journey this year {tags}",
]
NEUTRAL_TEMPLATES = [
    "Here's an update on my {topic} project, more details soon {tags}",
    "Sharing some notes on {topic} today {tags}",
    "A quick look at what I learned about {topic} this week {tags}",
    "Working on a new {topic} post, stay tuned {tags}",
    "Some thoughts on the current state of {topic} {tags}",
]
NEGATIVE_TEMPLATES = [
    "Really frustrated with how this {topic} launch turned out {tags}",
    "Disappointed by the recent {topic} changes, not a fan {tags}",
    "This {topic} issue has been such a headache to deal with {tags}",
    "Not happy with the {topic} experience today, needs work {tags}",
    "Struggling with {topic} problems again, so annoying {tags}",
]

TOPICS = ["python", "AI", "travel", "food", "fitness", "startup", "music",
          "gaming", "photography", "reading", "art", "productivity"]


def random_post(post_id, day):
    username = random.choice(USERNAMES)
    category = random.choice(CATEGORIES)
    possible_tags = CATEGORY_HASHTAGS[category] + random.sample(HASHTAG_POOL, 2)
    tags = random.sample(possible_tags, k=min(3, len(possible_tags)))
    tag_str = " ".join(sorted(set(tags)))

    sentiment_bucket = random.choices(
        ["pos", "neu", "neg"], weights=[0.45, 0.35, 0.20]
    )[0]
    template = random.choice(
        {"pos": POSITIVE_TEMPLATES, "neu": NEUTRAL_TEMPLATES,
         "neg": NEGATIVE_TEMPLATES}[sentiment_bucket]
    )
    content = template.format(topic=random.choice(TOPICS), tags=tag_str)

    # Posting time skewed toward common social-media active hours
    hour = random.choices(
        population=list(range(24)),
        weights=[1,1,1,1,1,2,3,4,5,6,7,8,9,8,7,6,7,8,9,10,9,7,4,2],
    )[0]
    minute = random.randint(0, 59)
    post_datetime = day.replace(hour=hour, minute=minute)

    likes = max(0, int(random.gauss(150, 120)))
    comments = max(0, int(random.gauss(15, 12)))
    shares = max(0, int(random.gauss(8, 7)))

    # Popular categories/sentiment get a small engagement boost
    if category == "Technology":
        likes = int(likes * 1.3)
    if sentiment_bucket == "pos":
        likes = int(likes * 1.15)

    return {
        "post_id": post_id,
        "username": username,
        "date": post_datetime.strftime("%Y-%m-%d"),
        "time": post_datetime.strftime("%H:%M"),
        "content": content,
        "hashtags": tag_str,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "category": category,
    }


def generate(num_posts=400, num_days=30, output_path="sample_posts.csv"):
    start_date = datetime.now() - timedelta(days=num_days)
    rows = []
    for i in range(1, num_posts + 1):
        day_offset = random.randint(0, num_days - 1)
        day = start_date + timedelta(days=day_offset)
        rows.append(random_post(i, day))

    rows.sort(key=lambda r: (r["date"], r["time"]))

    fieldnames = ["post_id", "username", "date", "time", "content",
                  "hashtags", "likes", "comments", "shares", "category"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} sample posts -> {output_path}")


if __name__ == "__main__":
    generate()
