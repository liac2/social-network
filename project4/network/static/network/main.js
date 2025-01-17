document.addEventListener('DOMContentLoaded', () => {

    const body = document.querySelector('.body');
    const section = document.querySelector('#new_post_div');
    let view = document.querySelector('.posts-view');


    // Create Post
    const btn = document.querySelector('#post_btn');
    if (btn !== null) {
        btn.onclick = (event) => {
            let input = document.querySelector('#new_post_input');
            const text = input.value;
            fetch('/post', {
                method: 'POST',
                body: JSON.stringify({
                    text: text
                })
            })
            .then(response => response.json())
            .then(result => {
                console.log(result);
                input.value = '';
            })
            .then(() => all_posts(section, view, body, 'all'));
        };
    }
    

    // All Posts by default
    if (view !== null) {
        all_posts(section, view, body, 'all');
    }
});

function profile (data, section, view, body) {

    // Hide old page
    if (section !== null) {
        section.style.display = 'none';
    }
    view.style.display = 'none';

    // Get data for user
    fetch(`/profile${data.id}`)
    .then(response => response.json())
    .then(d => {
        
        // Display follow btn
        let follow_btn = '';

        // Check if viewer can follow
        if (d.viewer.authenticated && d.viewer.email !== d.email) {
            if (d.viewer.following) {
                follow_btn = '<button data-follow="unfollow" class="btn-primary btn">Unfollow</button>';
            } else {
                follow_btn = '<button data-follow="follow" class="btn-primary btn">Follow</button>';
            }
        }

        // Display profile
        const page = document.querySelector('#profile');
        page.innerHTML = `<h1>${data.creator}</h1>
            <p id="followers">Followers: ${d.followers}</p>
            <p>Following: ${d.following}</p>
            ${follow_btn}
            <hr>
            <h2>Posts</h2>
            <div class="posts list-group"></div>`;
        
        // Follow btn logic
        if (d.viewer.authenticated && d.viewer.email !== d.email) {
            page.querySelector('button').onclick = (event) => {
                
                // Follow / Unfollow creator
                let element = event.target;
                let follow = false;
                if (element.dataset.follow === 'follow') {
                    follow = true;
                }

                // Send data to db
                fetch(`/profile${data.id}`, {
                    method: 'PUT',
                    body: JSON.stringify({
                        following: follow
                    })
                });

                // Edit data page displays
                let followers_p = page.querySelector('#followers');
                let text = followers_p.innerHTML.split(' ');
                let followers_count = parseInt(text[1]);
                let count = 0;
                if (follow) {
                    element.dataset.follow = 'unfollow';
                    element.innerHTML = 'Unfollow';
                    count++;
                } else {
                    element.dataset.follow = 'follow';
                    element.innerHTML = 'Follow';
                    count--;
                }
                followers_p.innerHTML = `${text[0]} ${followers_count + count}`;
            };
        }
        
        // Display users posts
        profile_posts_div = page.querySelector('.posts');
        for (let data of d.posts) {
            let entry = document.createElement('div');
            entry.className = 'list-group-item list-group-item-action list-group-item-light bg-light';
            entry.ariaCurrent = 'true';

            entry.innerHTML = `<div class="d-flex w-100 justify-content-between">
            <h5 class="mb-1">${data.creator}</h5>
            <small>${data.time}</small>
            </div>
            <p class="mb-1">${data.text}</p>
            <p class="mb-1">${data.likes}</p>`;

            // Append post to posts div
            profile_posts_div.append(entry);
        }

        // Append profile page to dom
        body.append(page);
    });
}

function all_posts (section, view, body, type) {
    view.innerHTML = '';
    fetch(`/post${type}`)
    .then(response => response.json())
    .then(posts => {

        // List all posts
        for (let data of posts) {
            let post = document.createElement('div');
            post.className = 'list-group-item list-group-item-action list-group-item-light bg-light';
            post.ariaCurrent = 'true';

            post.innerHTML = `<div class="d-flex w-100 justify-content-between">
            <h5 class="mb-1">${data.creator}</h5>
            <small>${data.time}</small>
            </div>
            <p class="mb-1">${data.text}</p>
            <p class="mb-1">${data.likes}</p>`;

            // Portfolio page
            const h5 = post.querySelector('h5');
            h5.onclick = () => profile(data, section, view, body);

            view.append(post);
        }

    });
}