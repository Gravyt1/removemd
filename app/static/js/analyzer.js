// analyzer.js
document.addEventListener('DOMContentLoaded', function() {
  const analyzeForm = document.getElementById('analyzeForm');
  const analyzeFileInput = document.getElementById('analyzeFileInput');
  const analyzeDropZone = document.getElementById('analyzeDropZone');
  const fileInfoContainer = document.getElementById('fileInfoContainer');
  const fileName = document.getElementById('fileName');
  const removeFileBtn = document.getElementById('removeFileBtn');
  const analyzeBtn = document.getElementById('analyzeBtn');
  const resultsSection = document.getElementById('resultsSection');
  const emptyState = document.getElementById('emptyState');
  const resultsContainer = document.getElementById('resultsContainer');
  const errorContainer = document.getElementById('errorContainer');
  const resultStatus = document.getElementById('resultStatus');
  const resultTitle = document.getElementById('resultTitle');
  const fileInfo = document.getElementById('fileInfo');
  const metadataContent = document.getElementById('metadataContent');
  
  let selectedFile = null;
  
  // Click on drop zone to trigger file input
  analyzeDropZone.addEventListener('click', () => {
    analyzeFileInput.click();
  });
  
  // Handle file selection
  analyzeFileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFileSelect(e.target.files[0]);
    }
  });
  
  // Drag and drop functionality
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    analyzeDropZone.addEventListener(eventName, preventDefaults, false);
  });
  
  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }
  
  ['dragenter', 'dragover'].forEach(eventName => {
    analyzeDropZone.addEventListener(eventName, highlight, false);
  });
  
  ['dragleave', 'drop'].forEach(eventName => {
    analyzeDropZone.addEventListener(eventName, unhighlight, false);
  });
  
  function highlight() {
    analyzeDropZone.classList.add('border-primary-500');
    analyzeDropZone.classList.remove('border-gray-600');
  }
  
  function unhighlight() {
    analyzeDropZone.classList.remove('border-primary-500');
    analyzeDropZone.classList.add('border-gray-600');
  }
  
  analyzeDropZone.addEventListener('drop', handleDrop, false);
  
  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }
  
  // Remove selected file
  removeFileBtn.addEventListener('click', () => {
    selectedFile = null;
    analyzeFileInput.value = '';
    fileInfoContainer.classList.add('hidden');
    analyzeBtn.disabled = true;
    resetResults();
  });
  
  // Form submission
  analyzeForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!selectedFile) {
      showError('Please select a file first.');
      return;
    }
    
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Analyzing...';
    resetResults();
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `Server returned ${response.status}`);
      }
      
      const data = await response.json();
      displayResults(data);
      
    } catch (error) {
      console.error('Error:', error);
      showError(error.message);
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = 'Analyze Metadata Now';
    }
  });
  
  function handleFileSelect(file) {
    selectedFile = file;
    fileName.textContent = file.name;
    fileInfoContainer.classList.remove('hidden');
    analyzeBtn.disabled = false;
    resetResults();
  }
  
  function displayResults(data) {
    // Show results section
    resultsSection.classList.remove('hidden');
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
    
    emptyState.classList.add('hidden');
    errorContainer.classList.add('hidden');
    resultsContainer.classList.remove('hidden');
    
    resultStatus.textContent = 'Analysis complete';
    resultStatus.classList.remove('text-gray-400');
    resultStatus.classList.add('text-green-400');
    
    resultTitle.innerHTML = `<span class="material-symbols-outlined text-primary-400 mr-2">analytics</span>Analysis: ${data.filename}`;
    
    // Display file info
    fileInfo.innerHTML = `
      <div class="text-gray-400">File name</div>
      <div class="text-gray-300">${data.filename}</div>
      <div class="text-gray-400">MIME type</div>
      <div class="text-gray-300">${data.mimetype || 'Unknown'}</div>
    `;
    
    // Display metadata in a formatted way
    if (data.metadata && typeof data.metadata === 'object' && Object.keys(data.metadata).length > 0) {
      metadataContent.innerHTML = formatMetadata(data.metadata);
    } else {
      metadataContent.innerHTML = `
        <div class="text-center py-8 text-gray-400">
          <span class="material-symbols-outlined text-3xl mb-2">check_circle</span>
          <p>No metadata found in this file</p>
        </div>
      `;
    }
  }
  
  function showError(message) {
    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth' });
    
    emptyState.classList.add('hidden');
    resultsContainer.classList.add('hidden');
    errorContainer.classList.remove('hidden');
    
    document.getElementById('errorMessage').textContent = message;
    resultStatus.textContent = 'Analysis failed';
    resultStatus.classList.remove('text-gray-400');
    resultStatus.classList.add('text-red-400');
  }
  
  function resetResults() {
    resultsSection.classList.add('hidden');
    emptyState.classList.remove('hidden');
    resultsContainer.classList.add('hidden');
    errorContainer.classList.add('hidden');
    
    resultStatus.textContent = 'No file analyzed';
    resultStatus.classList.remove('text-green-400', 'text-red-400');
    resultStatus.classList.add('text-gray-400');
  }
  
  function formatMetadata(metadata, level = 0) {
    let html = '';
    
    for (const [key, value] of Object.entries(metadata)) {
      if (value && typeof value === 'object') {
        html += `
          <div class="mb-2 ${level > 0 ? 'ml-4' : ''}">
            <div class="font-medium text-gray-300 flex items-center">
              <span class="material-symbols-outlined text-sm mr-1">expand_more</span>
              ${key}
            </div>
            <div class="pl-6 border-l border-gray-700 mt-1">
              ${formatMetadata(value, level + 1)}
            </div>
          </div>
        `;
      } else {
        html += `
          <div class="flex justify-between py-1 ${level > 0 ? 'text-sm' : ''}">
            <span class="text-gray-400 pr-4">${key}:</span>
            <span class="text-gray-300 text-right break-all">${value}</span>
          </div>
        `;
      }
    }
    
    return html;
  }
});