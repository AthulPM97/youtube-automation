A python script to remove shorts from your liked videos in Youtube. You should create an app at `https://console.cloud.google.com/` and get your `credentials.json` first.

YouTube assigns daily quota points to each project (usually 10,000 units/day by default).
Each videos.rate call (used to unlike) costs 50 quota units.
So you can only make ~200 unlikes per day before hitting the limit. Quota resets every 24 hours.
