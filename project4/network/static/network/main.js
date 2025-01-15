document.addEventListener('DOMContentLoaded', () => {

    // Create Post
    document.querySelector('#post_btn').onclick = (event) => {
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
        });
    };

    // All Posts
    let view = document.querySelector('.posts-view');
    fetch('/post')
    .then(response => response.json())
    .then(posts => {

        // List all posts
        for (let data of posts) {
            let post = document.createElement('a');
            post.className = 'list-group-item list-group-item-action list-group-item-light bg-light';
            post.dataset.id = data.id;
            post.href = '#';
            post.ariaCurrent = 'true';

            post.innerHTML = `<div class="d-flex w-100 justify-content-between">
            <h5 class="mb-1">${data.creator}</h5>
            <small>${data.time}</small>
            </div>
            <p class="mb-1">${data.text}</p>
            <p class="mb-1">${data.likes}</p>`;

            view.append(post);
        }

    });
});