(() => {
    const deleteNoteButtonId = "delete_note_button";
    const deleteNoteButton = document.getElementById(deleteNoteButtonId);

    const deleteNoteDialogId = "delete_note_dialog";
    const deleteNoteDialog = document.getElementById(deleteNoteDialogId);

    if (!deleteNoteButton) {
        console.error(`Could not find button with ID "${deleteNoteButtonId}".`);
        return;
    }

    deleteNoteButton.addEventListener("click", () => {
        if (!deleteNoteDialog) {
            console.error(
                `Could not find dialog with ID "${deleteNoteDialogId}".`,
            );
            return;
        }

        deleteNoteDialog.showModal();
    });

    deleteNoteDialog.addEventListener("click", (e) => {
        if (e.target === deleteNoteDialog) {
            deleteNoteDialog.close();
        }
    });
})();
