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
});