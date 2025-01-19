document.addEventListener('DOMContentLoaded', () => {

    window.body = document.querySelector('.body');
    window.section = document.querySelector('#new_post_div');
    window.own_view_btn = document.querySelector('#following_view_btn');
    window.view = document.querySelector('.posts-view');
    window.view_btn = document.querySelector('#all_posts_view_btn');
    window.profile_view = document.querySelector('#profile');

    // Create Post
    const btn = document.querySelector('#post_btn');
    if (btn) {
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
            .then(() => all_posts('all', 1));
        };
    }

    // Following view
    if (own_view_btn) {
        own_view_btn.onclick = (event) => {
            event.preventDefault();
            all_posts('following', 1)
        };
    }

    // All Posts
    if (view && view_btn) {
        all_posts('all', 1);
        view_btn.onclick = (event) => {
            event.preventDefault();
            all_posts('all', 1);
        } 
    }
});

function profile (data, page) {

    // Hide old page
    if (window.section !== null) {
        window.section.style.display = 'none';
    }
    window.view.style.display = 'none';

    window.profile_view.innerHTML = '';
    window.profile_view.style.display = 'block';

    // Get data for user
    fetch(`/profile?id=${data.id}&page=${page}`)
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
        page.innerHTML = `<h1>${d.email}</h1>
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
                fetch(`/profile?id=${data.id}`, {
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

        // Add pagination
        pagination(d.pagination, 'profile');

        // Append profile page to dom
        window.body.append(page);
    });
}

function all_posts (type, page) {

    // Setup page
    window.section && (window.section.style.display = 'block');
    window.view && ((window.view.style.display = 'block'), (window.view.innerHTML = ''));
    window.profile_view && (window.profile_view.innerHTML = '');


    fetch(`/post?type=${type}&page=${page}`)
    .then(response => response.json())
    .then(posts_data => {
        console.log(posts_data);

        // List all posts
        let posts = posts_data.posts
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
            h5.onclick = () => profile(data, 1);

            if (window.view) {
                window.view.append(post);
            } else {
                console.error('window.view ist undefined.');
            }
        }
        pagination(posts_data.pagination, type);

    });
}

