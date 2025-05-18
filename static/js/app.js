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

const questionRatingButtons = document.querySelectorAll('button[data-is-like]')

questionRatingButtons.forEach(item =>
    item.addEventListener('click', () => {
        const objectId = item.dataset.objectId
        const isLike = item.dataset.isLike
        const isQuestion = item.dataset.isQuestion

        if (item.classList.contains('active'))
            item.classList.remove('active')
        else {
            item.classList.add('active')
            const oppositeButton = [...questionRatingButtons].find(b =>
                b.dataset.objectId === objectId &&
                b.dataset.isQuestion === isQuestion &&
                b.dataset.isLike !== isLike
            );
            if (oppositeButton)
                oppositeButton.classList.remove('active')
        }

        fetch(`/like`, {
            method: "POST",
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            body: JSON.stringify({
                is_question: isQuestion === '1',
                is_like: isLike === '1',
                object_id: objectId
            }),
            mode: "same-origin"
        })
        .then(response =>
            response.json().then(data => {
                const counter = document.querySelector(`[data-object-rating-counter="${objectId}"]`)
                counter.innerHTML = data.rating
            })
        )
    })
)