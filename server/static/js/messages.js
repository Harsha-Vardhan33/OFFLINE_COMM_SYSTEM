/*
 * ============================================================
 * OFFLINE COMM SYSTEM
 * USER MESSAGING CLIENT
 * ============================================================
 *
 * User-to-user messaging frontend.
 *
 * Current functionality:
 *   - Load registered users
 *   - Select a user
 *   - Load private conversation
 *   - Send text messages
 *   - Poll conversation every 2 seconds
 *   - Store current identity in localStorage
 *
 * Backend:
 *   GET  /api/users
 *   POST /api/users
 *   GET  /api/messages
 *   POST /api/messages
 *   GET  /api/messages/conversation
 *
 * Future:
 *   - File transfer
 *   - Image transfer
 *   - Encryption
 *   - WebSocket/live delivery
 * ============================================================
 */

"use strict";


/* ============================================================
   API
   ============================================================ */

const API = {
    users: "/api/users",
    messages: "/api/messages",
    conversation: "/api/messages/conversation"
};


/* ============================================================
   APPLICATION STATE
   ============================================================ */

const state = {

    currentUser:
        localStorage.getItem(
            "offline_comm_user"
        ) || "",

    currentNode:
        localStorage.getItem(
            "offline_comm_node"
        ) || "",

    users: [],

    selectedUser: "",

    messages: [],

    pollingTimer: null,

    sending: false

};


/* ============================================================
   DOM HELPER
   ============================================================ */

function getElement(id) {

    return document.getElementById(id);

}


/* ============================================================
   HTML ESCAPING
   ============================================================ */

function escapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent =
        value ?? "";

    return div.innerHTML;

}


/* ============================================================
   INITIALS
   ============================================================ */

function getInitials(name) {

    const value =
        String(name || "").trim();

    if (!value) {

        return "--";

    }

    const parts =
        value.split(/\s+/);

    if (parts.length === 1) {

        return parts[0]
            .substring(0, 2)
            .toUpperCase();

    }

    return (
        parts[0].charAt(0) +
        parts[parts.length - 1].charAt(0)
    ).toUpperCase();

}


/* ============================================================
   USER NAME
   ============================================================ */

function getUserName(user) {

    if (!user) {

        return "";

    }

    return String(
        user.user_name ||
        user.name ||
        user.username ||
        ""
    ).trim();

}


/* ============================================================
   API REQUEST
   ============================================================ */

async function apiRequest(
    url,
    options = {}
) {

    const requestOptions = {
        ...options
    };


    if (
        requestOptions.body &&
        !requestOptions.headers
    ) {

        requestOptions.headers = {
            "Content-Type":
                "application/json"
        };

    }


    const response =
        await fetch(
            url,
            requestOptions
        );


    const contentType =
        response.headers.get(
            "content-type"
        ) || "";


    let data;


    if (
        contentType.includes(
            "application/json"
        )
    ) {

        data =
            await response.json();

    } else {

        data =
            await response.text();

    }


    if (!response.ok) {

        let errorMessage =
            "Request failed";


        if (
            data &&
            typeof data === "object"
        ) {

            errorMessage =
                data.error ||
                data.message ||
                errorMessage;

        } else if (data) {

            errorMessage =
                String(data);

        }


        throw new Error(
            errorMessage
        );

    }


    return data;

}


/* ============================================================
   IDENTITY
   ============================================================ */

function saveIdentity(
    userName,
    nodeId
) {

    state.currentUser =
        String(
            userName || ""
        ).trim();

    state.currentNode =
        String(
            nodeId || ""
        ).trim();


    if (state.currentUser) {

        localStorage.setItem(
            "offline_comm_user",
            state.currentUser
        );

    }


    if (state.currentNode) {

        localStorage.setItem(
            "offline_comm_node",
            state.currentNode
        );

    }

}


/* ============================================================
   UPDATE CURRENT USER DISPLAY
   ============================================================ */

function updateCurrentUserDisplay() {

    const name =
        state.currentUser ||
        "Local User";


    const initials =
        getInitials(name);


    const nameElement =
        getElement(
            "currentUserName"
        );


    if (nameElement) {

        nameElement.textContent =
            name;

    }


    const initialsElement =
        getElement(
            "currentUserInitials"
        );


    if (initialsElement) {

        initialsElement.textContent =
            initials;

    }


    const nodeElement =
        getElement(
            "currentNodeId"
        );


    if (nodeElement) {

        nodeElement.textContent =
            state.currentNode ||
            "LOCAL NODE";

    }

}


/* ============================================================
   LOAD IDENTITY FROM PAGE / LOCAL STORAGE
   ============================================================ */

function initializeIdentity() {

    const storedUser =
        localStorage.getItem(
            "offline_comm_user"
        ) || "";


    const storedNode =
        localStorage.getItem(
            "offline_comm_node"
        ) || "";


    saveIdentity(
        storedUser,
        storedNode
    );


    updateCurrentUserDisplay();

}


/* ============================================================
   STATUS MESSAGE
   ============================================================ */

function showStatus(
    message,
    isError = false
) {

    const possibleElements = [

        getElement(
            "messageStatus"
        ),

        getElement(
            "connectionStatus"
        ),

        getElement(
            "statusMessage"
        )

    ].filter(Boolean);


    for (
        const element of possibleElements
    ) {

        element.textContent =
            message;

        element.classList.toggle(
            "error",
            isError
        );

        element.classList.toggle(
            "success",
            !isError
        );

    }


    if (
        message &&
        possibleElements.length > 0
    ) {

        window.setTimeout(
            () => {

                for (
                    const element of possibleElements
                ) {

                    element.textContent =
                        "";

                    element.classList.remove(
                        "error",
                        "success"
                    );

                }

            },
            3000
        );

    }

}


/* ============================================================
   LOAD USERS
   ============================================================ */

async function loadUsers() {

    try {

        const data =
            await apiRequest(
                API.users
            );


        state.users =
            Array.isArray(data)
                ? data
                : (
                    Array.isArray(
                        data.users
                    )
                        ? data.users
                        : []
                );


        renderUsers();

        renderModalUsers();


    } catch (error) {

        console.error(
            "Unable to load users:",
            error
        );


        showStatus(
            "Unable to load users",
            true
        );

    }

}


/* ============================================================
   FILTER USERS
   ============================================================ */

function getOtherUsers() {

    return state.users.filter(
        user => {

            const name =
                getUserName(user);


            if (!name) {

                return false;

            }


            if (
                state.currentUser &&
                name.toLowerCase() ===
                state.currentUser.toLowerCase()
            ) {

                return false;

            }


            return true;

        }
    );

}


/* ============================================================
   RENDER CONVERSATION LIST
   ============================================================ */

function renderUsers() {

    const container =
        getElement(
            "conversationList"
        );


    if (!container) {

        return;

    }


    container.innerHTML = "";


    const users =
        getOtherUsers();


    const countElement =
        getElement(
            "conversationCount"
        );


    if (countElement) {

        countElement.textContent =
            String(users.length);

    }


    if (users.length === 0) {

        container.innerHTML = `
            <div class="empty-users">
                <strong>No other users connected</strong>
                <span>
                    Connect another device to start messaging.
                </span>
            </div>
        `;

        return;

    }


    for (
        const user of users
    ) {

        const name =
            getUserName(user);


        const button =
            document.createElement(
                "button"
            );


        button.type =
            "button";

        button.className =
            "user-item";


        if (
            name === state.selectedUser
        ) {

            button.classList.add(
                "active"
            );

        }


        const initials =
            getInitials(name);


        const nodeId =
            user.node_id ||
            "LOCAL NODE";


        button.innerHTML = `
            <span class="user-avatar">
                ${escapeHtml(initials)}
            </span>

            <span class="user-info">
                <strong>
                    ${escapeHtml(name)}
                </strong>

                <small>
                    ${escapeHtml(nodeId)}
                </small>
            </span>

            <span class="user-status-dot"></span>
        `;


        button.addEventListener(
            "click",
            () => {

                selectUser(name);

            }
        );


        container.appendChild(
            button
        );

    }

}


/* ============================================================
   RENDER MODAL USERS
   ============================================================ */

function renderModalUsers(
    searchText = ""
) {

    const container =
        getElement(
            "modalUserList"
        );


    if (!container) {

        return;

    }


    const search =
        String(
            searchText || ""
        )
        .trim()
        .toLowerCase();


    const users =
        getOtherUsers().filter(
            user => {

                const name =
                    getUserName(user)
                    .toLowerCase();

                return !search ||
                    name.includes(search);

            }
        );


    container.innerHTML = "";


    if (users.length === 0) {

        container.innerHTML = `
            <div class="empty-users">
                No matching users
            </div>
        `;

        return;

    }


    for (
        const user of users
    ) {

        const name =
            getUserName(user);


        const button =
            document.createElement(
                "button"
            );


        button.type =
            "button";

        button.className =
            "modal-user-item";


        button.innerHTML = `
            <span class="user-avatar">
                ${escapeHtml(
                    getInitials(name)
                )}
            </span>

            <span class="user-info">
                <strong>
                    ${escapeHtml(name)}
                </strong>

                <small>
                    Available on local network
                </small>
            </span>
        `;


        button.addEventListener(
            "click",
            async () => {

                closeNewConversationModal();

                await selectUser(name);

            }
        );


        container.appendChild(
            button
        );

    }

}


/* ============================================================
   SELECT USER
   ============================================================ */

async function selectUser(
    userName
) {

    const name =
        String(
            userName || ""
        ).trim();


    if (!name) {

        return;

    }


    if (
        state.currentUser &&
        name.toLowerCase() ===
        state.currentUser.toLowerCase()
    ) {

        return;

    }


    state.selectedUser =
        name;


    renderUsers();


    updateConversationHeader(
        name
    );


    enableComposer();


    await loadConversation();

}


/* ============================================================
   UPDATE CHAT HEADER
   ============================================================ */

function updateConversationHeader(
    userName
) {

    const user =
        state.users.find(
            item =>
                getUserName(item) ===
                userName
        );


    const avatar =
        getElement(
            "chatAvatar"
        );


    if (avatar) {

        avatar.textContent =
            getInitials(userName);

    }


    const nameElement =
        getElement(
            "chatUserName"
        );


    if (nameElement) {

        nameElement.textContent =
            userName;

    }


    const statusElement =
        getElement(
            "chatUserStatus"
        );


    if (statusElement) {

        const nodeId =
            user?.node_id ||
            "Local network";


        statusElement.textContent =
            `${nodeId} • Available`;

    }


    const infoAvatar =
        getElement(
            "infoAvatar"
        );


    if (infoAvatar) {

        infoAvatar.textContent =
            getInitials(userName);

    }


    const infoName =
        getElement(
            "infoUserName"
        );


    if (infoName) {

        infoName.textContent =
            userName;

    }


    const infoNode =
        getElement(
            "infoUserNode"
        );


    if (infoNode) {

        infoNode.textContent =
            user?.node_id ||
            "LOCAL NODE";

    }


    const infoStatus =
        getElement(
            "infoUserStatus"
        );


    if (infoStatus) {

        infoStatus.textContent =
            "ONLINE";

    }

}


/* ============================================================
   LOAD CONVERSATION
   ============================================================ */

async function loadConversation() {

    if (
        !state.currentUser ||
        !state.selectedUser
    ) {

        renderMessages([]);

        return;

    }


    try {

        const url =
            API.conversation +
            "?sender=" +
            encodeURIComponent(
                state.currentUser
            ) +
            "&receiver=" +
            encodeURIComponent(
                state.selectedUser
            );


        const data =
            await apiRequest(url);


        state.messages =
            Array.isArray(data)
                ? data
                : (
                    Array.isArray(
                        data.messages
                    )
                        ? data.messages
                        : []
                );


        renderMessages(
            state.messages
        );


    } catch (error) {

        console.error(
            "Unable to load conversation:",
            error
        );


        showStatus(
            "Unable to load conversation",
            true
        );

    }

}


/* ============================================================
   RENDER MESSAGES
   ============================================================ */

function renderMessages(
    messages
) {

    const container =
        getElement(
            "messageArea"
        );


    if (!container) {

        return;

    }


    container.innerHTML = "";


    if (!state.selectedUser) {

        container.innerHTML = `
            <div class="empty-conversation">
                <div class="empty-icon">
                    💬
                </div>

                <h2>
                    Select a conversation
                </h2>

                <p>
                    Select another user from the network
                    to start a private conversation.
                </p>
            </div>
        `;

        return;

    }


    if (
        !messages ||
        messages.length === 0
    ) {

        container.innerHTML = `
            <div class="empty-conversation">
                <div class="empty-icon">
                    💬
                </div>

                <h2>
                    Start your conversation
                </h2>

                <p>
                    Send a message to
                    <strong>
                        ${escapeHtml(
                            state.selectedUser
                        )}
                    </strong>
                    over the local network.
                </p>
            </div>
        `;

        return;

    }


    const fragment =
        document.createDocumentFragment();


    for (
        const message of messages
    ) {

        const sender =
            String(
                message.sender || ""
            );


        const text =
            String(
                message.message || ""
            );


        const outgoing =
            sender.toLowerCase() ===
            state.currentUser.toLowerCase();


        const row =
            document.createElement(
                "div"
            );


        row.className =
            outgoing
                ? "message-row outgoing"
                : "message-row incoming";


        const bubble =
            document.createElement(
                "div"
            );


        bubble.className =
            "message-bubble";


        const messageText =
            document.createElement(
                "div"
            );


        messageText.className =
            "message-text";

        messageText.textContent =
            text;


        const meta =
            document.createElement(
                "div"
            );


        meta.className =
            "message-meta";


        const time =
            document.createElement(
                "span"
            );


        time.textContent =
            formatTime(
                message.created_at
            );


        meta.appendChild(
            time
        );


        if (outgoing) {

            const status =
                document.createElement(
                    "span"
                );


            status.className =
                "message-status";


            status.textContent =
                message.status ||
                "SENT";


            meta.appendChild(
                status
            );

        }


        bubble.appendChild(
            messageText
        );

        bubble.appendChild(
            meta
        );

        row.appendChild(
            bubble
        );


        fragment.appendChild(
            row
        );

    }


    container.appendChild(
        fragment
    );


    requestAnimationFrame(
        () => {

            container.scrollTop =
                container.scrollHeight;

        }
    );

}


/* ============================================================
   FORMAT TIME
   ============================================================ */

function formatTime(
    value
) {

    if (!value) {

        return "";

    }


    const date =
        new Date(value);


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return String(value);

    }


    return date.toLocaleTimeString(
        [],
        {
            hour: "2-digit",
            minute: "2-digit"
        }
    );

}


/* ============================================================
   FIND MESSAGE INPUT
   ============================================================ */

function findMessageInput() {

    return (
        getElement("messageInput") ||
        getElement("messageText") ||
        getElement("message") ||
        getElement("chatInput")
    );

}


/* ============================================================
   ENABLE COMPOSER
   ============================================================ */

function enableComposer() {

    const input =
        findMessageInput();


    const sendButton =
        getElement(
            "sendButton"
        );


    if (input) {

        input.disabled =
            !state.selectedUser;

        input.placeholder =
            state.selectedUser
                ? `Message ${state.selectedUser}...`
                : "Select a user first...";

    }


    if (sendButton) {

        sendButton.disabled =
            !state.selectedUser;

    }

}


/* ============================================================
   SEND MESSAGE
   ============================================================ */

async function sendMessage() {

    if (state.sending) {

        return;

    }


    if (!state.currentUser) {

        showStatus(
            "No user identity found. Return to the portal.",
            true
        );

        return;

    }


    if (!state.currentNode) {

        /*
         * A node ID is useful but is not required
         * by the current backend.
         */

        state.currentNode = "";

    }


    if (!state.selectedUser) {

        showStatus(
            "Select a user first",
            true
        );

        return;

    }


    const input =
        findMessageInput();


    if (!input) {

        showStatus(
            "Message input not found",
            true
        );

        return;

    }


    const message =
        input.value.trim();


    if (!message) {

        return;

    }


    state.sending =
        true;


    const sendButton =
        getElement(
            "sendButton"
        );


    if (sendButton) {

        sendButton.disabled =
            true;

    }


    try {

        const payload = {

            node_id:
                state.currentNode ||
                null,

            sender:
                state.currentUser,

            receiver:
                state.selectedUser,

            message:
                message,

            message_type:
                "TEXT"

        };


        await apiRequest(
            API.messages,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify(
                        payload
                    )
            }
        );


        input.value = "";


        await loadConversation();


    } catch (error) {

        console.error(
            "Message send failed:",
            error
        );


        showStatus(
            error.message ||
            "Message could not be sent",
            true
        );

    } finally {

        state.sending =
            false;


        enableComposer();


        if (input) {

            input.focus();

        }

    }

}


/* ============================================================
   ENTER TO SEND
   ============================================================ */

function handleInputKeydown(
    event
) {

    if (
        event.key !== "Enter"
    ) {

        return;

    }


    if (
        event.shiftKey
    ) {

        return;

    }


    event.preventDefault();


    sendMessage();

}


/* ============================================================
   SEARCH USERS
   ============================================================ */

function connectUserSearch() {

    const input =
        getElement(
            "userSearch"
        );


    if (!input) {

        return;

    }


    input.addEventListener(
        "input",
        () => {

            const search =
                input.value
                    .trim()
                    .toLowerCase();


            const buttons =
                document.querySelectorAll(
                    "#conversationList .user-item"
                );


            for (
                const button of buttons
            ) {

                const text =
                    button.textContent
                        .toLowerCase();


                button.style.display =
                    text.includes(search)
                        ? ""
                        : "none";

            }

        }
    );

}


/* ============================================================
   MODAL SEARCH
   ============================================================ */

function connectModalSearch() {

    const input =
        getElement(
            "modalUserSearch"
        );


    if (!input) {

        return;

    }


    input.addEventListener(
        "input",
        () => {

            renderModalUsers(
                input.value
            );

        }
    );

}


/* ============================================================
   NEW CONVERSATION MODAL
   ============================================================ */

function openNewConversationModal() {

    const modal =
        getElement(
            "newConversationModal"
        );


    if (!modal) {

        return;

    }


    renderModalUsers();


    modal.classList.remove(
        "hidden"
    );


    const search =
        getElement(
            "modalUserSearch"
        );


    if (search) {

        search.value = "";

        window.setTimeout(
            () => search.focus(),
            50
        );

    }

}


function closeNewConversationModal() {

    const modal =
        getElement(
            "newConversationModal"
        );


    if (!modal) {

        return;

    }


    modal.classList.add(
        "hidden"
    );

}


/* ============================================================
   CONVERSATION INFO MODAL
   ============================================================ */

function openInfoModal() {

    if (!state.selectedUser) {

        return;

    }


    const modal =
        getElement(
            "infoModal"
        );


    if (!modal) {

        return;

    }


    modal.classList.remove(
        "hidden"
    );

}


function closeInfoModal() {

    const modal =
        getElement(
            "infoModal"
        );


    if (!modal) {

        return;

    }


    modal.classList.add(
        "hidden"
    );

}


/* ============================================================
   CONNECT MODALS
   ============================================================ */

function connectModals() {

    const newButton =
        getElement(
            "newConversationButton"
        );


    if (newButton) {

        newButton.addEventListener(
            "click",
            openNewConversationModal
        );

    }


    const closeButton =
        getElement(
            "closeModalButton"
        );


    if (closeButton) {

        closeButton.addEventListener(
            "click",
            closeNewConversationModal
        );

    }


    const modal =
        getElement(
            "newConversationModal"
        );


    if (modal) {

        const overlay =
            modal.querySelector(
                ".modal-overlay"
            );


        if (overlay) {

            overlay.addEventListener(
                "click",
                closeNewConversationModal
            );

        }

    }


    const infoButton =
        getElement(
            "conversationInfoButton"
        );


    if (infoButton) {

        infoButton.addEventListener(
            "click",
            openInfoModal
        );

    }


    const closeInfoButton =
        getElement(
            "closeInfoButton"
        );


    if (closeInfoButton) {

        closeInfoButton.addEventListener(
            "click",
            closeInfoModal
        );

    }


    const infoModal =
        getElement(
            "infoModal"
        );


    if (infoModal) {

        const overlay =
            infoModal.querySelector(
                ".modal-overlay"
            );


        if (overlay) {

            overlay.addEventListener(
                "click",
                closeInfoModal
            );

        }

    }

}


/* ============================================================
   CONNECT SEND BUTTON
   ============================================================ */

function connectSendButton() {

    const button =
        getElement(
            "sendButton"
        );


    if (!button) {

        return;

    }


    button.addEventListener(
        "click",
        sendMessage
    );

}


/* ============================================================
   CONNECT MESSAGE INPUT
   ============================================================ */

function connectMessageInput() {

    const input =
        findMessageInput();


    if (!input) {

        return;

    }


    input.addEventListener(
        "keydown",
        handleInputKeydown
    );

}


/* ============================================================
   CONNECT ATTACHMENT BUTTON
   ============================================================ */

function connectAttachmentButton() {

    const button =
        getElement(
            "attachmentButton"
        );


    const fileInput =
        getElement(
            "fileInput"
        );


    if (
        !button ||
        !fileInput
    ) {

        return;

    }


    button.addEventListener(
        "click",
        () => {

            fileInput.click();

        }
    );


    fileInput.addEventListener(
        "change",
        () => {

            if (
                fileInput.files &&
                fileInput.files.length > 0
            ) {

                showStatus(
                    "File transfer will be added next."
                );

            }

        }
    );

}


/* ============================================================
   CONNECT KEYBOARD SHORTCUTS
   ============================================================ */

function connectKeyboardShortcuts() {

    document.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Escape"
            ) {

                closeNewConversationModal();

                closeInfoModal();

            }

        }
    );

}


/* ============================================================
   POLLING
   ============================================================ */

function startPolling() {

    stopPolling();


    state.pollingTimer =
        window.setInterval(
            async () => {

                if (
                    state.selectedUser &&
                    !state.sending
                ) {

                    await loadConversation();

                }

            },
            2000
        );

}


function stopPolling() {

    if (
        state.pollingTimer
    ) {

        window.clearInterval(
            state.pollingTimer
        );

        state.pollingTimer =
            null;

    }

}


/* ============================================================
   REFRESH
   ============================================================ */

async function refreshConversation() {

    await loadUsers();

    await loadConversation();

}


/* ============================================================
   CONNECT REFRESH
   ============================================================ */

function connectRefreshButton() {

    const buttons = [

        getElement(
            "refreshButton"
        ),

        getElement(
            "refreshMessages"
        ),

        getElement(
            "refreshButtonMessages"
        )

    ].filter(Boolean);


    for (
        const button of buttons
    ) {

        button.addEventListener(
            "click",
            refreshConversation
        );

    }

}


/* ============================================================
   INITIAL USER SELECTION
   ============================================================ */

async function selectInitialUser() {

    const users =
        getOtherUsers();


    if (
        users.length === 0
    ) {

        renderMessages([]);

        return;

    }


    if (
        state.selectedUser &&
        users.some(
            user =>
                getUserName(user) ===
                state.selectedUser
        )
    ) {

        await selectUser(
            state.selectedUser
        );

        return;

    }


    /*
     * Do not automatically select a user.
     *
     * The user should explicitly choose
     * who they want to communicate with.
     */

    renderMessages([]);

    enableComposer();

}


/* ============================================================
   INITIALIZATION
   ============================================================ */

async function initializeMessaging() {

    console.log(
        "OFFLINE COMM messaging client starting..."
    );


    initializeIdentity();

    connectSendButton();

    connectMessageInput();

    connectUserSearch();

    connectModalSearch();

    connectModals();

    connectAttachmentButton();

    connectKeyboardShortcuts();

    connectRefreshButton();

    enableComposer();


    await loadUsers();


    await selectInitialUser();


    startPolling();


    console.log(
        "OFFLINE COMM messaging client ready."
    );

}


/* ============================================================
   START APPLICATION
   ============================================================ */

if (
    document.readyState ===
    "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        initializeMessaging
    );

} else {

    initializeMessaging();

}
