function changeProfileImage() {
  document.getElementById('id_photo').click();
}

function previewImage(event) {
  var reader = new FileReader();
  reader.onload = function () {
    var output = document.getElementById('profileImage');
    output.src = reader.result;

    document.getElementById('editBtn').style.display = 'none';
    document.getElementById('saveBtn').style.display = 'inline-block';
  };
  reader.readAsDataURL(event.target.files[0]);
}
document.addEventListener('DOMContentLoaded', function () {
    const editBtn = document.getElementById('editBtn');
    const saveBtn = document.getElementById('saveBtn');
    const fullNameField = document.getElementById('full_name');
    const fullNameInput = document.getElementById('id_full_name');
    const bioField = document.getElementById('bio');
    const bioInput = document.getElementById('id_bio');

    // When Edit button is clicked
    editBtn.addEventListener('click', function () {
        // Show input fields and hide the span text
        fullNameField.style.display = 'none';
        fullNameInput.style.display = 'inline-block';
        bioField.style.display = 'none';
        bioInput.style.display = 'block';

        saveBtn.style.display = 'inline-block';
        editBtn.style.display = 'none';
    });

    // When Save button is clicked (only for style changes)
    saveBtn.addEventListener('click', function () {
        // Show text fields again and hide the input fields
        fullNameField.style.display = 'inline';
        fullNameInput.style.display = 'none';
        bioField.style.display = 'inline';
        bioInput.style.display = 'none';

        saveBtn.style.display = 'none';
        editBtn.style.display = 'inline-block';
    });
});
document.addEventListener("DOMContentLoaded", function () {
    const inputFile = document.getElementById("id_photo");
    const profileImage = document.getElementById("profileImage");
    const cropModal = document.getElementById("crop-modal");
    const cropContainer = document.getElementById("image-to-crop");
    const cropButton = document.getElementById("crop-button");
    let cropper;

    inputFile.addEventListener("change", function (event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                cropContainer.src = e.target.result;
                cropModal.style.display = "flex";

                if (cropper) {
                    cropper.destroy();
                }

                cropper = new Cropper(cropContainer, {
                    aspectRatio: 1,
                    viewMode: 1,
                });
            };
            reader.readAsDataURL(file);
        }
    });

    cropButton.addEventListener("click", function (e) {
        e.preventDefault();
        if (!cropper) return;

        const canvas = cropper.getCroppedCanvas({ width: 1400, height: 1400 });
        canvas.toBlob(function (blob) {
            const file = new File([blob], "cropped.jpg", { type: "image/jpeg" });

            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            inputFile.files = dataTransfer.files;

            profileImage.src = URL.createObjectURL(blob);
            cropModal.style.display = "none";
            cropper.destroy();
        }, "image/jpeg");
    });
});

function changeProfileImage() {
    document.getElementById("id_photo").click();
}