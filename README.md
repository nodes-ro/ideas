# https://ideas.nodes.ro

> Share your idea. Upvote the ideas that you like. Spark creativity.

---

## Source Code

[![GitHub][fi=github]][source]

[source]: https://github.com/nodes-ro/ideas.git
[fi=github]: https://img.shields.io/badge/GitHub-Source%20Code-blue?logo=github

---

## Problem / Solution

**Problem:** Gathering and prioritizing community ideas can be scattered, making it hard to find and develop the best suggestions.

**Solution:** A lightweight platform to submit new ideas, browse existing ones, and upvote favorites—surface the top concepts and foster collaborative creativity.

---

## Key Features

Whether you're searching for your next big idea or eager to share your creativity with others, this platform empowers you to do just that. It's a dynamic hub where innovative minds converge to spark breakthrough concepts and foster collaborative growth.

- **Submit Ideas:** Quickly add a title and description for each idea.  
- **Upvote System:** Vote on ideas you like to help surface popular suggestions.  
- **Browse & Filter:** View all ideas and sort by newest or most upvoted.  
- **Responsive Design:** Accessible on desktop and mobile devices.  
- **Support Page:** Learn how to contribute, donate, or provide feedback.  

---

## Support

Your support keeps the platform running and evolving:

- **Donate** 
- **Spread the Word:** Share with friends, teams, or communities.  
- **Provide Feedback:** Let us know your suggestions or report issues.  

---

## Demo

- **Live Site:** https://ideas.nodes.ro  

---

## Build & Run Docker Image

### 1. Remove any existing image
> docker rmi -f ideas:0.0.1

### 2. Build the new image (must be run from the directory containing your Dockerfile)
> docker build -t ideas:0.0.1 .

### 3. Run the container
-e OPENAI_API_KEY="sk-proj-..." => Sets an environment variable inside the container.
-p 8005:8005 => Publishes (maps) port 8005 on the host machine to port 8005 in the container.
-v /home/user/ideas.nodes.ro/data/ideas.db:/app/instance/ideas.db => Mounts a file (or directory) from the host into the container.
-d => Runs the container in detached mode (in the background).
ideas:0.0.1 => The name and tag of the Docker image to run.

> docker run -e OPENAI_API_KEY="sk-proj-..." -p 8005:8005 -v /home/user/ideas.nodes.ro/data/ideas.db:/app/instance/ideas.db  -d ideas:0.0.1 
