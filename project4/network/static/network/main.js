document.addEventListener('DOMContentLoaded', () => {

    window.body = document.querySelector('.body');
    window.section = document.querySelector('#new_post_div');
    window.own_view_btn = document.querySelector('#following_view_btn');
    window.view = document.querySelector('.posts-view');
    window.view_btn = document.querySelector('#all_posts_view_btn');
    window.profile_view = document.querySelector('#profile');

    // Enable history in website
    window.onpopstate = (event) => {
        if (event.state.view === 'profile'){
            profile(event.state.data, event.state.page)
        } else {
            all_posts(event.state.type, event.state.page)
        }
    }
    window.onload = () => {
        if (history.state) {
            console.log(`refresh ${history.state.view}`);
            if (history.state.view === 'profile'){
                profile(history.state.data, history.state.page)
            } else {
                all_posts(history.state.type, history.state.page)
            }
        } else {
            console.log('reload index');
            all_posts('all', 1);
        }
        
    }

    // Create Post
    const btn = document.querySelector('#post_btn');
    if (btn) {
        btn.onclick = (event) => {
            let input = document.querySelector('#new_post_input');
            const text = input.value;
            fetch('api/posts/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') 
                },
                credentials: 'include',
                body: JSON.stringify({
                    text: text
                })
            })
            .then(response => response.json())
            .then(result => {
                console.log('all: ');
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

function profile (data, page_num) {

    // Hide old page
    if (window.section !== null) {
        window.section.style.display = 'none';
    }
    window.view.style.display = 'none';

    window.profile_view.innerHTML = '';
    window.profile_view.style.display = 'block';



    // Get data for user
    fetch(`api/posts/${data.id}/profile/?page=${page_num}`)
    .then(response => response.json())
    .then(d => {

        // Website History 
        history.pushState({view: 'profile', data: data, page: page_num}, "", `#profile/${d.viewer.email}`);
        
        // Display follow btn
        let follow_btn = '';

        // Check if viewer can follow
        if (d.viewer.authenticated && d.viewer.email !== d.profile.email) {
            if (d.profile.followed_by_user) {
                follow_btn = '<button data-follow="unfollow" class="btn-primary btn">Unfollow</button>';
            } else {
                follow_btn = '<button data-follow="follow" class="btn-primary btn">Follow</button>';
            }
        }

        // Display profile
        profile_data = d.profile
        const page = document.querySelector('#profile');
        page.innerHTML = `<h1>${profile_data.email}</h1>
            <p id="followers">Followers: ${profile_data.followers}</p>
            <p>Following: ${profile_data.following}</p>
            ${follow_btn}
            <hr>
            <h2>Posts</h2>
            <div class="posts list-group"></div>`;
        
        // Follow btn logic
        if (d.viewer.authenticated && d.viewer.email !== d.profile.email) {
            page.querySelector('button').onclick = (event) => {
                
                // Follow / Unfollow creator
                let element = event.target;
                let follow = false;
                if (element.dataset.follow === 'follow') {
                    follow = true;
                }

                // Send data to db
                fetch(`api/posts/${data.id}/profile/follow/`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken') 
                    },
                    credentials: 'include',
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
        for (let all_data of d.posts) {

            let data = all_data.post
            let entry = document.createElement('div');
            entry.className = 'list-group-item list-group-item-action list-group-item-light bg-light';
            entry.ariaCurrent = 'true';

            entry.innerHTML = `<div class="d-flex w-100 justify-content-between">
            <h5 class="mb-1">${data.creator}</h5>
            <small>${data.time}</small>
            </div>
            <p class="mb-1 text">${data.text}</p>
            <div class="row justify-content-between">
                <div class="col-md-auto likes_div">
                    <i data-like="${all_data.liked}" class="fs-6 text-danger icon-heart bi bi-heart${all_data.liked ? '-fill' : ''}"></i>
                    <p class="mb-1 fs-6 fw-medium likes_count d-inline">${data.likes}</p>
                </div>
            </div>`;

             // Edit btn
             if (d.viewer.authenticated && d.viewer.email === data.creator) {
                let likes_div = entry.querySelector('.likes_div');

                // Create div for btn
                let edit_div = entry.querySelector('.edit_btn_div');
                if (!edit_div) {
                    let edit_div = document.createElement('div');
                    edit_div.className = 'col-md-auto edit_btn_div';
                    edit_div.innerHTML = `<button data-type="edit" class="edit_btn btn btn-outline-primary">
                        <i class="bi bi-pencil-fill"></i>
                        Edit
                    </button>`;
                    likes_div.insertAdjacentElement('afterend', edit_div);
                }
                
                edit_post(entry, data);
            }

            // Likes btn
            if (d.viewer.authenticated){
                like_post(entry, data);
            }

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


    fetch(`api/posts/${type}?page=${page}`)
    .then(response => response.json())
    .then(posts_data => {
        console.log(posts_data);

        history.pushState({view: 'allposts', page: page, type: type}, "", `#${type}`);

        // List all posts
        let posts = posts_data.posts
        for (let all_data of posts) {

            let data = all_data.post
            let post = document.createElement('div');
            post.className = 'list-group-item list-group-item-action list-group-item-light bg-light';
            post.ariaCurrent = 'true';

            post.innerHTML = `<div class="d-flex w-100 justify-content-between">
            <h5 class="mb-1">${data.creator}</h5>
            <small>${data.time}</small>
            </div>
            <p class="mb-1 text">${data.text}</p>
            <div class="row justify-content-between">
                <div class="col-md-auto likes_div">
                    <i data-like="${all_data.liked}" class="fs-6 text-danger icon-heart bi bi-heart${all_data.liked ? '-fill' : ''}"></i>
                    <p class="mb-1 fs-6 fw-medium likes_count d-inline">${data.likes}</p>
                </div>
            </div>`;


            // Likes btn
            if (posts_data.viewer.authenticated){
                like_post(post, data);
            }
            

            // Edit btn
            if (posts_data.viewer.authenticated && posts_data.viewer.email === data.creator) {
                let likes_div = post.querySelector('.likes_div');

                // Create div for btn
                let edit_div = post.querySelector('.edit_btn_div');
                if (!edit_div) {
                    let edit_div = document.createElement('div');
                    edit_div.className = 'col-md-auto edit_btn_div';
                    edit_div.innerHTML = `<button data-type="edit" class="edit_btn btn btn-outline-primary">
                        <i class="bi bi-pencil-fill"></i>
                        Edit
                    </button>`;
                    likes_div.insertAdjacentElement('afterend', edit_div);
                }
                
                edit_post(post, data);
            }
            

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

function edit_post (post, data) {
    const edit_btn = post.querySelector('.edit_btn');

    edit_btn.onclick = (event) => {

        let text = post.querySelector('.text');

        // Edit the post
        if (edit_btn.dataset.type === 'edit') {
            
            // Add textarea with initial text
            text.style.display = 'none';
            let tarea = document.createElement('textarea');
            tarea.className = 'form-control my-1';
            tarea.value = text.innerHTML;
            text.insertAdjacentElement('afterend', tarea);

            // Edit btn to save
            edit_btn.innerHTML = '<i class="bi bi-save"></i> Save';
            edit_btn.className = 'edit_btn btn btn-primary';
            edit_btn.dataset.type = 'save';
        
        // Save new version
        } else {
            let tarea = post.querySelector('textarea');
            text.innerHTML = tarea.value;
            text.style.display = 'block';
            tarea.remove();

            // Edit btn to edit
            edit_btn.innerHTML = '<i class="bi bi-pencil-fill"></i> Edit';
            edit_btn.className = 'edit_btn btn btn-outline-primary';
            edit_btn.dataset.type = 'edit';

            // Send new post to server
            fetch(`api/posts/${data.id}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') 
                },
                credentials: 'include',
                body: JSON.stringify({
                    text: text.innerHTML,
                    id: data.id
                })
            });
        }
    };
}

function like_post(post, data) {
    let heart = post.querySelector('.icon-heart');
    let likes = post.querySelector('.likes_count');
    let likes_count = parseInt(likes.textContent);
    if (heart) {
        heart.onclick = () => {
            let liked = heart.dataset.like === 'true';
            if (!liked) {
                likes_count++;
                liked = !liked;
                heart.dataset.like = liked.toString();
                heart.className = 'text-danger icon-heart bi bi-heart-fill';
            } else {
                likes_count--;
                liked = !liked;
                heart.dataset.like = liked.toString();
                heart.className = 'text-danger icon-heart bi bi-heart';
            }
            likes.textContent = likes_count.toString();
    
            // Send data to db
            fetch(`api/posts/${data.id}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') 
                },
                credentials: 'include',
                body: JSON.stringify({
                    liked: liked
                })
            });
        };
        // Add animation to heart
        heart.addEventListener('mouseover', () => {
            heart.className = 'text-danger icon-heart bi bi-heart-fill';
        });
        heart.addEventListener('mouseout', () => {
            if (heart.dataset.like === 'false') {
                heart.className = 'text-danger icon-heart bi bi-heart';
            }
        });
    }


}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
