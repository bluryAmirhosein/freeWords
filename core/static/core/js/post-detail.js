function addComment() {
    const commentInput = document.getElementById('id_content');
    const commentText = commentInput.value.trim();
        if (commentText) {
          const commentList = document.getElementById('id_content');
          const newComment = document.createElement('p');
          newComment.innerHTML = `<b>You:</b> ${commentText}`;
          commentList.appendChild(newComment);
          commentInput.value = '';
        } else {
          alert('Please write a comment before posting.');
        }
      }
function toggleEditForm(commentId) {
    const form = document.getElementById(`edit-form-${commentId}`);
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}
function toggleReplyForm(commentId) {
    const form = document.getElementById(`reply-form-${commentId}`);
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

    function toggleEditReplyForm(replyId) {
    const form = document.getElementById(`edit-reply-form-${replyId}`);
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

function deleteComment(commentId) {
    const commentElement = document.getElementById(`comment-${commentId}`);
    commentElement.remove();
}

document.getElementById("share-button").addEventListener("click", function() {
    if (navigator.share) {
        navigator.share({
            title: document.title,  // عنوان پست
            text: "Check out this blog post!",  // توضیحات اختیاری
            url: window.location.href  // لینک پست جاری
        })
        .then(() => console.log("Post shared successfully"))
        .catch((error) => console.log("Error sharing post:", error));
    } else {
        alert("Sharing is not supported on this device.");
    }
});
