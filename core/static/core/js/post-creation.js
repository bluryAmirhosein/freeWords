  CKEDITOR.replace('id_description', {
    toolbar: 'full',
    height: 300,
    extraPlugins: 'uploadimage',
  });

  document.getElementById('id_cover_image').addEventListener('change', function (event) {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const image = document.getElementById('image-to-crop');
        image.src = e.target.result;
        document.getElementById('crop-modal').style.display = 'flex';

        const cropper = new Cropper(image, {
          aspectRatio: 7 / 2,
          viewMode: 1,
        });

        document.getElementById('crop-button').onclick = function (e) {
          e.preventDefault();
          const canvas = cropper.getCroppedCanvas();
          canvas.toBlob(function (blob) {
            // Create a new File object from the cropped image
            const croppedFile = new File([blob], 'cropped-image.jpg', { type: 'image/jpeg' });

            // Create a new FileList and assign the cropped file to it
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(croppedFile);

            // Assign the FileList to the hidden input
            const croppedImageInput = document.getElementById('cropped-image-input');
            croppedImageInput.files = dataTransfer.files;

            // Hide the modal and destroy the cropper instance
            document.getElementById('crop-modal').style.display = 'none';
            cropper.destroy();
          }, 'image/jpeg');
        };
      };
      reader.readAsDataURL(file);
    }
  });

  const titleInput = document.getElementById('id_title_heading');
  const slugInput = document.getElementById('id_slug');

  titleInput.addEventListener('input', () => {
    slugInput.value = titleInput.value.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9\-]/g, '');
  });