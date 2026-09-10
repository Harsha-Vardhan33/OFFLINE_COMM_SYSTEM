/*
 * ============================================================
 * OFFLINE COMM SYSTEM
 * USER CAPTIVE PORTAL
 * ============================================================
 *
 * Flow:
 *
 *   Phone / Laptop Browser
 *          |
 *          v
 *     Captive Portal
 *          |
 *          | POST /api/users
 *          v
 *     Flask Server
 *          |
 *          v
 *       SQLite
 *          |
 *          v
 *       /messages
 *
 * The browser stores only its local identity.
 *
 * IMPORTANT:
 * Node ID is ALWAYS a plain string.
 * API responses are NEVER inserted into the Node ID field.
 * ============================================================
 */

"use strict";


/* ============================================================
   CONSTANTS
   ============================================================ */

const USER_STORAGE_KEY =
    "offline_comm_user";

const NODE_STORAGE_KEY =
    "offline_comm_node";

const REGISTRATION_STORAGE_KEY =
    "offline_comm_registration";


/*
 * Change this version whenever this file is changed.
 *
 * portal.html also contains a cache-busting version.
 */

const PORTAL_VERSION =
    "20260831-03";


/* ============================================================
   DOM ELEMENTS
   ============================================================ */

const joinForm =
    document.getElementById("joinForm");

const userNameInput =
    document.getElementById("userName");

const nodeIdInput =
    document.getElementById("nodeId");

const joinButton =
    document.getElementById("joinButton");

const portalMessage =
    document.getElementById("portalMessage");


/* ============================================================
   MESSAGE DISPLAY
   ============================================================ */

function showMessage(
    message,
    type = "error"
) {

    if (!portalMessage) {
        return;
    }

    portalMessage.hidden = false;

    portalMessage.textContent =
        message;

    portalMessage.className =
        `portal-message ${type}`;
}


function hideMessage() {

    if (!portalMessage) {
        return;
    }

    portalMessage.hidden = true;

    portalMessage.textContent = "";

    portalMessage.className =
        "portal-message";
}


/* ============================================================
   BUTTON STATE
   ============================================================ */

function setButtonLoading(
    loading
) {

    if (!joinButton) {
        return;
    }

    joinButton.disabled =
        loading;

    joinButton.textContent =
        loading
            ? "Joining..."
            : "Join System";
}


/* ============================================================
   NODE ID VALIDATION
   ============================================================ */

/*
 * A valid Node ID must be a normal identifier.
 *
 * Examples:
 *
 * PHONE_01
 * PHONE_TEST_01
 * LAPTOP_01
 * ESP32_01
 *
 * JSON is explicitly rejected.
 */

function isValidNodeId(
    nodeId
) {

    if (
        typeof nodeId !== "string"
    ) {
        return false;
    }

    const value =
        nodeId.trim();

    if (!value) {
        return false;
    }

    if (
        value.length < 2 ||
        value.length > 64
    ) {
        return false;
    }

    /*
     * Reject JSON/object-like values.
     */

    if (
        value.startsWith("{") ||
        value.startsWith("[")
    ) {
        return false;
    }

    /*
     * Only allow simple device identifiers.
     */

    return /^[A-Za-z0-9_-]+$/.test(
        value
    );
}


/* ============================================================
   GENERATE DEVICE NODE ID
 * ============================================================ */

/*
 * We do NOT use data from /api/nodes to create the Node ID.
 *
 * The browser generates its own stable identifier.
 *
 * Example:
 *
 * PHONE_A3F91C2D
 *
 * It is stored in localStorage and reused when the
 * same browser returns to the network.
 */

function generateNodeId() {

    let randomPart = "";

    try {

        if (
            window.crypto &&
            window.crypto.getRandomValues
        ) {

            const bytes =
                new Uint8Array(4);

            window.crypto.getRandomValues(
                bytes
            );

            randomPart =
                Array.from(bytes)
                    .map(
                        byte =>
                            byte
                                .toString(16)
                                .padStart(
                                    2,
                                    "0"
                                )
                    )
                    .join("")
                    .toUpperCase();

        }

    } catch (error) {

        console.warn(
            "Crypto API unavailable.",
            error
        );

    }


    /*
     * Fallback for older browsers.
     */

    if (!randomPart) {

        randomPart =
            Math.random()
                .toString(36)
                .substring(
                    2,
                    10
                )
                .toUpperCase();

    }


    return `PHONE_${randomPart}`;
}


/* ============================================================
   GET OR CREATE LOCAL NODE ID
   ============================================================ */

function getLocalNodeId() {

    const savedNode =
        localStorage.getItem(
            NODE_STORAGE_KEY
        );


    /*
     * Only use the saved value if it is actually
     * a valid Node ID.
     */

    if (
        isValidNodeId(
            savedNode
        )
    ) {

        return savedNode.trim();

    }


    /*
     * IMPORTANT:
     *
     * If an older version stored JSON in localStorage,
     * remove it instead of displaying it.
     */

    localStorage.removeItem(
        NODE_STORAGE_KEY
    );


    const newNodeId =
        generateNodeId();


    localStorage.setItem(
        NODE_STORAGE_KEY,
        newNodeId
    );


    return newNodeId;
}


/* ============================================================
   RESTORE USER IDENTITY
   ============================================================ */

function restoreIdentity() {

    const savedUser =
        localStorage.getItem(
            USER_STORAGE_KEY
        );


    const nodeId =
        getLocalNodeId();


    /*
     * Restore user name if available.
     */

    if (
        userNameInput &&
        savedUser
    ) {

        userNameInput.value =
            savedUser;

    }


    /*
     * ALWAYS put only the plain Node ID
     * into the input.
     */

    if (nodeIdInput) {

        nodeIdInput.value =
            nodeId;

    }


    console.log(
        "Local device identity:",
        {
            user:
                savedUser || null,

            node_id:
                nodeId
        }
    );
}


/* ============================================================
   VALIDATE FORM
   ============================================================ */

function validateForm() {

    const userName =
        userNameInput
            ? userNameInput.value.trim()
            : "";


    const nodeId =
        nodeIdInput
            ? nodeIdInput.value.trim()
            : "";


    if (!userName) {

        return {
            valid: false,
            message:
                "Please enter your name."
        };

    }


    if (
        userName.length < 2
    ) {

        return {
            valid: false,
            message:
                "Your name must contain at least 2 characters."
        };

    }


    if (
        userName.length > 80
    ) {

        return {
            valid: false,
            message:
                "Your name is too long."
        };

    }


    if (
        !isValidNodeId(
            nodeId
        )
    ) {

        return {
            valid: false,
            message:
                "Invalid Node ID. Use a simple ID such as PHONE_01."
        };

    }


    return {
        valid: true,
        userName,
        nodeId
    };
}


/* ============================================================
   POST JSON
   ============================================================ */

async function postJSON(
    url,
    payload
) {

    console.log(
        "POST",
        url,
        payload
    );


    const response =
        await fetch(
            `${url}?v=${PORTAL_VERSION}`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",

                    "Accept":
                        "application/json"
                },

                body:
                    JSON.stringify(
                        payload
                    ),

                cache:
                    "no-store"
            }
        );


    /*
     * Read text first.
     *
     * This avoids JSON.parse errors when the
     * server returns a non-JSON error page.
     */

    const text =
        await response.text();


    let data = null;


    if (text) {

        try {

            data =
                JSON.parse(
                    text
                );

        } catch (error) {

            console.error(
                "Invalid JSON response:",
                text
            );

            throw new Error(
                "Server returned an invalid response."
            );
        }
    }


    if (!response.ok) {

        const errorMessage =
            data &&
            (
                data.error ||
                data.message
            );


        throw new Error(
            errorMessage ||
            `Request failed with HTTP ${response.status}.`
        );
    }


    return data;
}


/* ============================================================
   REGISTER USER
   ============================================================ */

async function registerUser(
    userName,
    nodeId
) {

    /*
     * IMPORTANT:
     *
     * Only these two values are sent.
     *
     * No node object.
     * No /api/nodes response.
     * No dashboard data.
     */

    const payload = {

        user_name:
            userName,

        node_id:
            nodeId

    };


    return await postJSON(
        "/api/users",
        payload
    );
}


/* ============================================================
   JOIN SYSTEM
   ============================================================ */

async function joinSystem(
    event
) {

    event.preventDefault();


    hideMessage();


    const validation =
        validateForm();


    if (!validation.valid) {

        showMessage(
            validation.message,
            "error"
        );

        return;
    }


    const userName =
        validation.userName;

    const nodeId =
        validation.nodeId;


    setButtonLoading(
        true
    );


    try {

        console.log(
            "Joining OFFLINE_COMM:",
            {
                user_name:
                    userName,

                node_id:
                    nodeId
            }
        );


        const result =
            await registerUser(
                userName,
                nodeId
            );


        console.log(
            "Registration response:",
            result
        );


        /*
         * Store local identity.
         */

        localStorage.setItem(
            USER_STORAGE_KEY,
            userName
        );


        localStorage.setItem(
            NODE_STORAGE_KEY,
            nodeId
        );


        /*
         * Store server registration response
         * for the messaging page/session.
         */

        if (result) {

            localStorage.setItem(
                REGISTRATION_STORAGE_KEY,
                JSON.stringify(
                    result
                )
            );

        }


        showMessage(
            "Connected. Opening messages...",
            "success"
        );


        /*
         * Go to the actual user application.
         */

        window.setTimeout(
            function () {

                window.location.href =
                    "/messages";

            },
            350
        );


    } catch (error) {

        console.error(
            "Join error:",
            error
        );


        showMessage(
            error.message ||
            "Unable to join the local network.",
            "error"
        );


        setButtonLoading(
            false
        );
    }
}


/* ============================================================
   REMOVE INVALID LEGACY NODE DATA
   ============================================================ */

/*
 * Older versions of the project may have stored a JSON
 * object inside offline_comm_node.
 *
 * Clean it automatically.
 */

function cleanLegacyNodeStorage() {

    const storedNode =
        localStorage.getItem(
            NODE_STORAGE_KEY
        );


    if (!storedNode) {
        return;
    }


    if (
        !isValidNodeId(
            storedNode
        )
    ) {

        console.warn(
            "Removing invalid legacy Node ID:",
            storedNode
        );


        localStorage.removeItem(
            NODE_STORAGE_KEY
        );
    }
}


/* ============================================================
   FORM EVENT
   ============================================================ */

if (joinForm) {

    joinForm.addEventListener(
        "submit",
        joinSystem
    );

}


/* ============================================================
   INITIALIZATION
   ============================================================ */

cleanLegacyNodeStorage();

restoreIdentity();


console.log(
    "OFFLINE COMM portal ready."
);

console.log(
    "Portal version:",
    PORTAL_VERSION
);
