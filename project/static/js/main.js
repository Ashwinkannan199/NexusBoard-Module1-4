// Connect to the WebSocket server
const socket = io();

// Wait for the DOM to be fully loaded before running the script
document.addEventListener('DOMContentLoaded', () => {

    // --- Module 4: Socket.IO Setup ---
    const boardContainer = document.querySelector('.board-container');
    const boardId = boardContainer.dataset.boardId;

    // Emit 'join_board' event to server
    if (boardId) {
        socket.emit('join_board', { 'board_id': boardId });
    }
    
    // --- (Module 3 Code) ---
    const draggables = document.querySelectorAll('.card');
    const containers = document.querySelectorAll('.list-column');

    draggables.forEach(draggable => {
        draggable.addEventListener('dragstart', () => {
            draggable.classList.add('dragging');
        });

        draggable.addEventListener('dragend', () => {
            draggable.classList.remove('dragging');
        });
    });

    containers.forEach(container => {
        container.addEventListener('dragover', e => {
            e.preventDefault();
            const draggable = document.querySelector('.dragging');
            if (!draggable) return;

            const cardContainer = container.querySelector('.card-container');
            if (!cardContainer) return;
            
            container.classList.add('drag-over');
            const afterElement = getDragAfterElement(cardContainer, e.clientY);

            if (afterElement == null) {
                cardContainer.appendChild(draggable);
            } else {
                cardContainer.insertBefore(draggable, afterElement);
            }
        });

        container.addEventListener('dragleave', () => {
            container.classList.remove('drag-over');
        });

        // --- Module 4: Modify Drop Handler ---
        container.addEventListener('drop', e => {
            container.classList.remove('drag-over');
            
            // Find the card that was just dropped
            const draggable = document.querySelector('.dragging');
            if (!draggable) return;

            // Find its new list and its new sibling
            const newCardContainer = draggable.closest('.card-container');
            const afterElement = getDragAfterElement(newCardContainer, e.clientY);
            const nextSibling = afterElement ? afterElement : null;

            // Prepare data payload for the server
            const data = {
                'card_id': draggable.id,
                'new_list_id': newCardContainer.id,
                'next_sibling_id': nextSibling ? nextSibling.id : null
            };

            // Emit the 'card_moved' event to the server
            socket.emit('card_moved', data);
        });
    });

    function getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.card:not(.dragging)')];

        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;

            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }


    // --- Module 4: Add Socket.IO Listener ---
    
    /**
     * Listens for 'card_update_broadcast' events from the server.
     * This event is fired when *another* user moves a card.
     * We must then manually move the card on our own screen.
     */
    socket.on('card_update_broadcast', (data) => {
        console.log('Broadcast received:', data);

        const { card_id, new_list_id, next_sibling_id } = data;

        const card = document.getElementById(card_id);
        const newList = document.getElementById(new_list_id);

        if (!card || !newList) {
            console.error('Error: Card or List not found on this page.');
            return;
        }

        // Find the sibling to insert before
        const nextSibling = next_sibling_id ? document.getElementById(next_sibling_id) : null;

        // Perform the same DOM manipulation as the drag-and-drop
        if (nextSibling) {
            newList.insertBefore(card, nextSibling);
        } else {
            // If no sibling, append to the end of the list
            newList.appendChild(card);
        }
    });

    // Optional: Add a listener for when the page is unloaded
    window.addEventListener('beforeunload', () => {
        if (boardId) {
            socket.emit('leave_board', { 'board_id': boardId });
        }
    });

});