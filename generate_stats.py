import urllib.request, json, os, datetime

token = os.environ['GH_TOKEN']
username = "AnanthAkshay"

to_dt   = datetime.datetime.utcnow()
from_dt = to_dt - datetime.timedelta(days=365)

query = json.dumps({"query": """
{
  user(login: "%s") {
    contributionsCollection(from: "%s", to: "%s") {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date contributionCount }
        }
      }
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalPullRequestReviewContributions
    }
  }
}
""" % (username, from_dt.strftime('%Y-%m-%dT%H:%M:%SZ'), to_dt.strftime('%Y-%m-%dT%H:%M:%SZ'))}).encode()

req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=query,
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
)
with urllib.request.urlopen(req) as r:
    data = json.loads(r.read())

col      = data['data']['user']['contributionsCollection']
cal      = col['contributionCalendar']
total    = cal['totalContributions']
commits  = col['totalCommitContributions']
prs      = col['totalPullRequestContributions']
issues   = col['totalIssueContributions']
reviews  = col['totalPullRequestReviewContributions']

# Build flat sorted list of (date, count)
days = sorted(
    (day['date'], day['contributionCount'])
    for week in cal['weeks']
    for day in week['contributionDays']
)

today = datetime.date.today()

# Current streak (walk backwards, skip today if 0)
current_streak = 0
for date_str, count in reversed(days):
    d = datetime.date.fromisoformat(date_str)
    if d > today:
        continue
    if count > 0:
        current_streak += 1
    elif d == today:
        continue   # today not over yet
    else:
        break

# Longest streak
longest_streak, run = 0, 0
for _, count in days:
    if count > 0:
        run += 1
        longest_streak = max(longest_streak, run)
    else:
        run = 0

svg = f"""<svg width="495" height="210" viewBox="0 0 495 210" xmlns="http://www.w3.org/2000/svg">
  <style>
    text {{ font-family: 'Segoe UI', Ubuntu, sans-serif; }}
  </style>

  <rect width="495" height="210" rx="10" fill="#1a1b27" stroke="#414868" stroke-width="1"/>

  <!-- Title -->
  <text x="25" y="32" font-size="14" font-weight="600" fill="#38bdae">&#128202; GitHub Stats · Last 365 Days</text>
  <line x1="25" y1="44" x2="470" y2="44" stroke="#414868" stroke-width="0.5"/>

  <!-- Top row dividers -->
  <line x1="165" y1="58" x2="165" y2="128" stroke="#414868" stroke-width="0.5"/>
  <line x1="330" y1="58" x2="330" y2="128" stroke="#414868" stroke-width="0.5"/>

  <!-- Commits (left) -->
  <text x="82" y="91" font-size="22" font-weight="700" fill="#bb9af7" text-anchor="middle">{commits}</text>
  <text x="82" y="112" font-size="11" fill="#a9b1d6" text-anchor="middle">Commits</text>

  <!-- Total Contributions (center) -->
  <text x="247" y="91" font-size="28" font-weight="700" fill="#70a5fd" text-anchor="middle">{total}</text>
  <text x="247" y="112" font-size="11" fill="#a9b1d6" text-anchor="middle">Total Contributions</text>

  <!-- PRs (right) -->
  <text x="412" y="91" font-size="22" font-weight="700" fill="#bb9af7" text-anchor="middle">{prs}</text>
  <text x="412" y="112" font-size="11" fill="#a9b1d6" text-anchor="middle">Pull Requests</text>

  <!-- Middle divider -->
  <line x1="25" y1="133" x2="470" y2="133" stroke="#414868" stroke-width="0.5"/>

  <!-- Bottom row dividers -->
  <line x1="165" y1="143" x2="165" y2="198" stroke="#414868" stroke-width="0.5"/>
  <line x1="330" y1="143" x2="330" y2="198" stroke="#414868" stroke-width="0.5"/>

  <!-- Current Streak -->
  <text x="82" y="168" font-size="20" font-weight="700" fill="#f7768e" text-anchor="middle">&#128293; {current_streak}</text>
  <text x="82" y="188" font-size="11" fill="#a9b1d6" text-anchor="middle">Current Streak</text>

  <!-- Longest Streak -->
  <text x="247" y="168" font-size="20" font-weight="700" fill="#e0af68" text-anchor="middle">&#127942; {longest_streak}</text>
  <text x="247" y="188" font-size="11" fill="#a9b1d6" text-anchor="middle">Longest Streak</text>

  <!-- Issues + Reviews -->
  <text x="412" y="163" font-size="13" fill="#9ece6a" text-anchor="middle">{issues} Issues</text>
  <text x="412" y="183" font-size="13" fill="#9ece6a" text-anchor="middle">{reviews} Reviews</text>
</svg>"""

with open("contribution-stats.svg", "w") as f:
    f.write(svg)

print(f"✅ {total} contributions | {commits} commits | {prs} PRs | streak: {current_streak} | longest: {longest_streak}")
