document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    const fileListContainer = document.getElementById('fileListContainer');
    const fileList = document.getElementById('fileList');
    const removeMetadataBtn = document.getElementById('removeMetadataBtn');
    
    let selectedFiles = [];

    // Drag and drop handling
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropZone.classList.add('border-primary-500');
        dropZone.classList.remove('border-gray-600');
    }

    function unhighlight() {
        dropZone.classList.remove('border-primary-500');
        dropZone.classList.add('border-gray-600');
    }

    dropZone.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    // Handle click on the drop zone
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    // Handle file selection via input
    fileInput.addEventListener('change', () => {
        handleFiles(fileInput.files);
    });

    // Process selected files
    function handleFiles(files) {
        selectedFiles = Array.from(files);
        updateFileList();
    }

    // Update the displayed file list
    function updateFileList() {
        fileList.innerHTML = '';
        
        if (selectedFiles.length > 0) {
            fileListContainer.classList.remove('hidden');
            
            selectedFiles.forEach((file, index) => {
                const listItem = document.createElement('li');
                listItem.className = 'flex justify-between items-center p-2 bg-gray-700 rounded mb-1';
                
                const fileNameSpan = document.createElement('span');
                fileNameSpan.textContent = file.name;
                fileNameSpan.className = 'truncate max-w-xs';
                
                const removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.innerHTML = '&times;';
                removeBtn.className = 'text-red-400 hover:text-red-300 ml-2';
                removeBtn.onclick = () => removeFile(index);
                
                listItem.appendChild(fileNameSpan);
                listItem.appendChild(removeBtn);
                fileList.appendChild(listItem);
            });
        } else {
            fileListContainer.classList.add('hidden');
        }
    }

    // Remove a file from the list
    function removeFile(index) {
        selectedFiles.splice(index, 1);
        updateFileList();
        
        // Update file input (not directly editable)
        const dataTransfer = new DataTransfer();
        selectedFiles.forEach(file => dataTransfer.items.add(file));
        fileInput.files = dataTransfer.files;
    }

    // Form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (selectedFiles.length === 0) {
            alert('Please select at least one file.');
            return;
        }
        
        // Disable button during processing
        removeMetadataBtn.disabled = true;
        removeMetadataBtn.textContent = 'Processing...';
        
        // Create a FormData and append the files
        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('file', file);
        });
        
        // Send files to the server
        fetch('/api/remove', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server error: ' + response.status);
            }
            return response.blob();
        })
        .then(blob => {
            // Create a download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            
            // Set filename depending on response type
            if (selectedFiles.length === 1) {
                a.download = 'cleaned_' + selectedFiles[0].name;
            } else {
                a.download = 'cleaned_files.zip';
            }
            
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            
            // Reset form
            selectedFiles = [];
            fileInput.value = '';
            updateFileList();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while processing your files. Please try again.');
        })
        .finally(() => {
            // Re-enable button
            removeMetadataBtn.disabled = false;
            removeMetadataBtn.textContent = 'Remove Metadata Now';
        });
    });
});
