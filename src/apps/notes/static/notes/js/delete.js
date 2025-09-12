(() => {
    const deleteNoteButtonId = "delete_note_button";
    const deleteNoteButton = document.getElementById(deleteNoteButtonId);

    if (!deleteNoteButton) {
        console.error(`Could not find button with ID "${deleteNoteButtonId}".`);
        return;
    }

    deleteNoteButton.addEventListener("click", () => {
        const deleteNoteDialogId = "delete_note_dialog";
        const deleteNoteDialog = document.getElementById(deleteNoteDialogId);

        if (!deleteNoteDialog) {
            console.error(
                `Could not find dialog with ID "${deleteNoteDialogId}".`,
            );
            return;
        }

        deleteNoteDialog.showModal();
    });
})();
