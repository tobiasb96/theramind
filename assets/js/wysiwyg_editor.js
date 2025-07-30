import {Editor} from 'https://esm.sh/@tiptap/core@2.6.6';
import StarterKit from 'https://esm.sh/@tiptap/starter-kit@2.6.6';
import Underline from 'https://esm.sh/@tiptap/extension-underline@2.6.6';

window.initWysiwygEditor = function (editorId, content, placeholder = 'Text eingeben...') {
  const editorElement = document.getElementById(editorId);
  const hiddenInput = document.getElementById(editorId + '-input');

  if (editorElement && !editorElement.hasAttribute('data-editor-initialized')) {
    editorElement.setAttribute('data-editor-initialized', 'true');

    // Initialize TipTap editor
    const editor = new Editor({
      element: editorElement,
      extensions: [
        StarterKit,
        Underline,
      ],
      content: content || `<p>${placeholder}</p>`,
      editorProps: {
        attributes: {
          class: 'format format-sm focus:outline-none format-blue max-w-none',
        },
      },
      onUpdate: ({editor}) => {
        // Update hidden input with current content
        hiddenInput.value = editor.getHTML();
      },
    });

    // Toolbar button event listeners with proper event handling
    document.getElementById('toggleBoldButton-' + editorId)?.addEventListener('click', (e) => {
      e.preventDefault();
      editor.chain().focus().toggleBold().run();
    });

    document.getElementById('toggleItalicButton-' + editorId)?.addEventListener('click', (e) => {
      e.preventDefault();
      editor.chain().focus().toggleItalic().run();
    });

    document.getElementById('toggleUnderlineButton-' + editorId)?.addEventListener('click', (e) => {
      e.preventDefault();
      editor.chain().focus().toggleUnderline().run();
    });

    document.getElementById('toggleListButton-' + editorId)?.addEventListener('click', (e) => {
      e.preventDefault();
      editor.chain().focus().toggleBulletList().run();
    });

    document.getElementById('toggleOrderedListButton-' + editorId)?.addEventListener('click', (e) => {
      e.preventDefault();
      editor.chain().focus().toggleOrderedList().run();
    });

    document.getElementById('toggleParagraphButton-' + editorId)?.addEventListener('click', (e) => {
      e.preventDefault();
      editor.chain().focus().setParagraph().run();
      // Hide dropdown using Flowbite instance
      const typographyDropdown = window.FlowbiteInstances?.getInstance('Dropdown', 'typographyDropdown-' + editorId);
      if (typographyDropdown) {
        typographyDropdown.hide();
      }
    });

    // Heading buttons
    document.querySelectorAll('.heading-button-' + editorId).forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        const level = parseInt(button.getAttribute('data-heading-level'));
        editor.chain().focus().toggleHeading({level}).run();
        // Hide dropdown using Flowbite instance
        const typographyDropdown = window.FlowbiteInstances?.getInstance('Dropdown', 'typographyDropdown-' + editorId);
        if (typographyDropdown) {
          typographyDropdown.hide();
        }
      });
    });

    // Initialize hidden input with current content
    hiddenInput.value = editor.getHTML();
  }
};

window.initSessionNotesExtras = function () {
  let autoSaveTimeout;
  const autosaveResponse = document.getElementById('autosave-response');
  const sessionNotesForm = document.getElementById('session-notes-form');

  if (sessionNotesForm && autosaveResponse) {
    // Function to trigger auto-save
    function triggerAutoSave() {
      clearTimeout(autoSaveTimeout);
      autoSaveTimeout = setTimeout(() => {
        // Get the editor content and update hidden input
        const editorElement = document.getElementById('session-notes-editor');
        const hiddenInput = document.getElementById('session-notes-editor-input');

        if (editorElement && hiddenInput) {
          // Update hidden input with current editor content
          hiddenInput.value = editorElement.innerHTML;

          // Show saving indicator
          autosaveResponse.innerHTML = `
                        <div class="flex items-center text-sm text-gray-500">
                            <svg class="w-4 h-4 mr-1 animate-spin" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            <span>Wird gespeichert...</span>
                        </div>
                    `;

          // Submit the form via HTMX
          htmx.trigger(sessionNotesForm, 'submit');
        }
      }, 2000); // 2 second delay
    }

    // Wait for the editor to be initialized, then set up event listeners
    setTimeout(() => {
      const editorElement = document.getElementById('session-notes-editor');
      if (editorElement) {
        // Listen for input events on the contenteditable div
        editorElement.addEventListener('input', function () {
          triggerAutoSave();
        });

        editorElement.addEventListener('keyup', function () {
          triggerAutoSave();
        });

        // Also use MutationObserver for more comprehensive change detection
        const observer = new MutationObserver(function (mutations) {
          let shouldTrigger = false;
          mutations.forEach(function (mutation) {
            if (mutation.type === 'childList' || mutation.type === 'characterData') {
              shouldTrigger = true;
            }
          });
          if (shouldTrigger) {
            triggerAutoSave();
          }
        });

        observer.observe(editorElement, {
          childList: true,
          subtree: true,
          characterData: true
        });
      }
    }, 1000);
  }

  // Show saving indicator when HTMX request starts
  document.body.addEventListener('htmx:beforeRequest', function (evt) {
    if (evt.detail.elt.id === 'session-notes-form') {
      autosaveResponse.innerHTML = `
                <div class="flex items-center text-sm text-gray-500">
                    <svg class="w-4 h-4 mr-1 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Wird gespeichert...</span>
                </div>
            `;
    }
  });

  // Show success indicator when HTMX request completes
  document.body.addEventListener('htmx:afterRequest', function (evt) {
    if (evt.detail.elt.id === 'session-notes-form') {

      if (evt.detail.xhr.status === 200) {
        autosaveResponse.innerHTML = `
                    <div class="flex items-center text-sm text-green-600">
                        <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                        </svg>
                        <span>Gesichert</span>
                    </div>
                `;

        // Hide the indicator after 3 seconds
        setTimeout(() => {
          autosaveResponse.innerHTML = '';
        }, 3000);
      } else {
        autosaveResponse.innerHTML = `
                    <div class="flex items-center text-sm text-red-600">
                        <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd"/>
                        </svg>
                        <span>Fehler beim Speichern</span>
                    </div>
                `;

        setTimeout(() => {
          autosaveResponse.innerHTML = '';
        }, 5000);
      }
    }
  });

  // Copy to clipboard logic
  const editorElement = document.getElementById('session-notes-editor');
  const copyNotesBtn = document.getElementById('copy-notes-btn');
  if (copyNotesBtn && editorElement) {
    copyNotesBtn.onclick = null; // Remove previous
    copyNotesBtn.addEventListener('click', function () {
      // Get formatted text content preserving line breaks and structure
      let textContent = '';
      const processNode = (node) => {
        if (node.nodeType === Node.TEXT_NODE) {
          return node.textContent;
        } else if (node.nodeType === Node.ELEMENT_NODE) {
          let result = '';
          const tagName = node.tagName.toLowerCase();
          if ([
            'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
          ].includes(tagName)) {
            if (result.length > 0) result += '\n';
          }
          for (let child of node.childNodes) {
            result += processNode(child);
          }
          if ([
            'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
          ].includes(tagName)) {
            result += '\n';
          } else if (tagName === 'br') {
            result += '\n';
          } else if (tagName === 'li') {
            result = '• ' + result + '\n';
          }
          return result;
        }
        return '';
      };
      textContent = processNode(editorElement);
      textContent = textContent.replace(/\n\s*\n\s*\n/g, '\n\n').trim();
      if (!textContent.trim()) {
        alert('Kein Inhalt zum Kopieren verfügbar.');
        return;
      }
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(textContent).then(() => {
          showCopySuccess();
        }).catch(() => {
          copyWithFallback(textContent);
        });
      } else {
        copyWithFallback(textContent);
      }

      function copyWithFallback(text) {
        const tempTextarea = document.createElement('textarea');
        tempTextarea.value = text;
        document.body.appendChild(tempTextarea);
        tempTextarea.select();
        document.execCommand('copy');
        document.body.removeChild(tempTextarea);
        showCopySuccess();
      }

      function showCopySuccess() {
        const originalText = copyNotesBtn.innerHTML;
        copyNotesBtn.innerHTML = `
                    <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                    </svg>
                    Kopiert!`;
        setTimeout(() => {
          copyNotesBtn.innerHTML = originalText;
        }, 2000);
      }
    });
  }
};

window.initReportExtras = function () {
  let autoSaveTimeout;
  const autosaveResponse = document.getElementById('autosave-response');
  const reportContentForm = document.getElementById('report-content-form');

  if (reportContentForm && autosaveResponse) {
    // Function to trigger auto-save
    function triggerAutoSave() {
      clearTimeout(autoSaveTimeout);
      autoSaveTimeout = setTimeout(() => {
        // Get the editor content and update hidden input
        const editorElement = document.getElementById('report-content-editor');
        const hiddenInput = document.getElementById('report-content-editor-input');

        if (editorElement && hiddenInput) {
          // Update hidden input with current editor content
          hiddenInput.value = editorElement.innerHTML;

          // Show saving indicator
          autosaveResponse.innerHTML = `
                        <div class="flex items-center text-sm text-gray-500">
                            <svg class="w-4 h-4 mr-1 animate-spin" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            <span>Wird gespeichert...</span>
                        </div>
                    `;

          // Submit the form via HTMX
          htmx.trigger(reportContentForm, 'submit');
        }
      }, 2000); // 2 second delay
    }

    // Wait for the editor to be initialized, then set up event listeners
    setTimeout(() => {
      const editorElement = document.getElementById('report-content-editor');
      if (editorElement) {
        // Listen for input events on the contenteditable div
        editorElement.addEventListener('input', function () {
          triggerAutoSave();
        });

        editorElement.addEventListener('keyup', function () {
          triggerAutoSave();
        });

        // Also use MutationObserver for more comprehensive change detection
        const observer = new MutationObserver(function (mutations) {
          let shouldTrigger = false;
          mutations.forEach(function (mutation) {
            if (mutation.type === 'childList' || mutation.type === 'characterData') {
              shouldTrigger = true;
            }
          });
          if (shouldTrigger) {
            triggerAutoSave();
          }
        });

        observer.observe(editorElement, {
          childList: true,
          subtree: true,
          characterData: true
        });
      }
    }, 1000);
  }

  // Show saving indicator when HTMX request starts
  document.body.addEventListener('htmx:beforeRequest', function (evt) {
    if (evt.detail.elt.id === 'report-content-form') {
      autosaveResponse.innerHTML = `
                <div class="flex items-center text-sm text-gray-500">
                    <svg class="w-4 h-4 mr-1 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Wird gespeichert...</span>
                </div>
            `;
    }
  });

  // Show success indicator when HTMX request completes
  document.body.addEventListener('htmx:afterRequest', function (evt) {
    if (evt.detail.elt.id === 'report-content-form') {

      if (evt.detail.xhr.status === 200) {
        autosaveResponse.innerHTML = `
                    <div class="flex items-center text-sm text-green-600">
                        <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                        </svg>
                        <span>Gesichert</span>
                    </div>
                `;

        // Hide the indicator after 3 seconds
        setTimeout(() => {
          autosaveResponse.innerHTML = '';
        }, 3000);
      } else {
        autosaveResponse.innerHTML = `
                    <div class="flex items-center text-sm text-red-600">
                        <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd"/>
                        </svg>
                        <span>Fehler beim Speichern</span>
                    </div>
                `;

        setTimeout(() => {
          autosaveResponse.innerHTML = '';
        }, 5000);
      }
    }
  });

  // Copy content to clipboard
  document.getElementById('copy-content-btn').addEventListener('click', function () {
    // Get the content from the WYSIWYG editor
    const editorElement = document.getElementById('report-content-editor');

    if (editorElement) {
      // Get formatted text content preserving line breaks and structure
      let textContent = '';

      // Process the content to preserve formatting
      const processNode = (node) => {
        if (node.nodeType === Node.TEXT_NODE) {
          return node.textContent;
        } else if (node.nodeType === Node.ELEMENT_NODE) {
          let result = '';
          const tagName = node.tagName.toLowerCase();

          // Add line breaks for block elements
          if (['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(tagName)) {
            if (result.length > 0) result += '\n';
          }

          // Process child nodes
          for (let child of node.childNodes) {
            result += processNode(child);
          }

          // Add line breaks after block elements
          if (['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(tagName)) {
            result += '\n';
          } else if (tagName === 'br') {
            result += '\n';
          } else if (tagName === 'li') {
            result = '• ' + result + '\n';
          }

          return result;
        }
        return '';
      };

      textContent = processNode(editorElement);

      // Clean up multiple line breaks and trim
      textContent = textContent.replace(/\n\s*\n\s*\n/g, '\n\n').trim();

      // Check if there's content to copy
      if (!textContent.trim()) {
        alert('Kein Inhalt zum Kopieren verfügbar.');
        return;
      }

      // Use modern clipboard API if available, fallback to old method
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(textContent).then(() => {
          showCopySuccess();
        }).catch(() => {
          // Fallback to old method
          copyWithFallback(textContent);
        });
      } else {
        copyWithFallback(textContent);
      }
    }

    function copyWithFallback(text) {
      // Create a temporary textarea to copy the text content
      const tempTextarea = document.createElement('textarea');
      tempTextarea.value = text;
      document.body.appendChild(tempTextarea);
      tempTextarea.select();
      document.execCommand('copy');
      document.body.removeChild(tempTextarea);
      showCopySuccess();
    }

    function showCopySuccess() {
      // Show success message
      const copyBtn = document.getElementById('copy-content-btn');
      const originalText = copyBtn.innerHTML;
      copyBtn.innerHTML = `
            <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
            Kopiert!
        `;

      setTimeout(() => {
        copyBtn.innerHTML = originalText;
      }, 2000);
    }
  });
}