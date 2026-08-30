/*
 * OFFLINE COMM SYSTEM
 * Dashboard Controller
 */

"use strict";

const API = {
    health: "/api/health",
    nodes: "/api/nodes",
    messages: "/api/messages",
    sos: "/api/sos",
    locations: "/api/locations",
    resources: "/api/resources"
};


/* ============================================================
   HELPERS
   ============================================================ */

async function fetchJSON(url) {

    const response = await fetch(url, {
        cache: "no-store"
    });

    if (!response.ok) {
        throw new Error(
            `${response.status} ${response.statusText}`
        );
    }

    return response.json();
}


function escapeHTML(value) {

    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function formatTime(value) {

    if (!value) {
        return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString();
}


function setText(id, value) {

    const element = document.getElementById(id);

    if (element) {
        element.textContent = value;
    }
}


/* ============================================================
   SERVER STATUS
   ============================================================ */

async function loadHealth() {

    const sidebarStatus =
        document.getElementById("sidebarServerStatus");

    const sidebarDot =
        document.getElementById("sidebarServerDot");

    const serverStatus =
        document.getElementById("serverStatus");

    const serverDot =
        document.getElementById("serverDot");

    try {

        const data = await fetchJSON(API.health);

        if (serverStatus) {
            serverStatus.textContent = "Server online";
        }

        if (sidebarStatus) {
            sidebarStatus.textContent = "Online";
        }

        if (serverDot) {
            serverDot.classList.add("online");
        }

        if (sidebarDot) {
            sidebarDot.classList.add("online");
        }

        setText(
            "lastUpdated",
            `Last updated: ${formatTime(data.time)}`
        );

    } catch (error) {

        if (serverStatus) {
            serverStatus.textContent = "Server unavailable";
        }

        if (sidebarStatus) {
            sidebarStatus.textContent = "Offline";
        }

        if (serverDot) {
            serverDot.classList.remove("online");
        }

        if (sidebarDot) {
            sidebarDot.classList.remove("online");
        }

        console.error(
            "Health check failed:",
            error
        );
    }
}


/* ============================================================
   NODES
   ============================================================ */

async function loadNodes() {

    const container =
        document.getElementById("nodeGrid");

    if (!container) {
        return;
    }

    try {

        const nodes = await fetchJSON(API.nodes);

        const online =
            nodes.filter(
                node => node.status === "ONLINE"
            ).length;

        setText("onlineNodes", online);
        setText("totalNodes", nodes.length);

        if (nodes.length === 0) {

            container.innerHTML = `
                <div class="empty">
                    No nodes registered.
                </div>
            `;

            return;
        }

        container.innerHTML = nodes.map(node => {

            const status =
                escapeHTML(node.status || "UNKNOWN");

            const battery =
                node.battery !== null &&
                node.battery !== undefined
                    ? `${Number(node.battery).toFixed(0)}%`
                    : "—";

            const signal =
                node.signal_strength !== null &&
                node.signal_strength !== undefined
                    ? `${Number(node.signal_strength).toFixed(0)} dBm`
                    : "—";

            return `
                <article class="node-card">

                    <div class="node-card-header">

                        <div>
                            <strong>
                                ${escapeHTML(node.node_name)}
                            </strong>

                            <small>
                                ${escapeHTML(node.node_id)}
                            </small>
                        </div>

                        <span class="status-badge">
                            ${status}
                        </span>

                    </div>

                    <div class="node-details">

                        <div>
                            <span>IP</span>
                            <strong>
                                ${escapeHTML(node.ip_address)}
                            </strong>
                        </div>

                        <div>
                            <span>Battery</span>
                            <strong>${battery}</strong>
                        </div>

                        <div>
                            <span>Signal</span>
                            <strong>${signal}</strong>
                        </div>

                        <div>
                            <span>Role</span>
                            <strong>
                                ${escapeHTML(node.role)}
                            </strong>
                        </div>

                    </div>

                    <small class="node-last-seen">
                        Last seen:
                        ${formatTime(node.last_seen)}
                    </small>

                </article>
            `;

        }).join("");

    } catch (error) {

        container.innerHTML = `
            <div class="empty">
                Unable to load nodes.
            </div>
        `;

        console.error(
            "Node loading failed:",
            error
        );
    }
}


/* ============================================================
   MESSAGES
   ============================================================ */

async function loadMessages() {

    const container =
        document.getElementById("messageList");

    if (!container) {
        return;
    }

    try {

        const messages =
            await fetchJSON(API.messages);

        setText(
            "totalMessages",
            messages.length
        );

        if (messages.length === 0) {

            container.innerHTML = `
                <div class="empty">
                    No messages available.
                </div>
            `;

            return;
        }

        const recent =
            [...messages]
                .sort(
                    (a, b) =>
                        new Date(b.created_at) -
                        new Date(a.created_at)
                )
                .slice(0, 10);

        container.innerHTML = recent.map(message => {

            return `
                <article class="message-item">

                    <div class="message-header">

                        <strong>
                            ${escapeHTML(message.sender)}
                        </strong>

                        <span class="status-badge">
                            ${escapeHTML(message.status)}
                        </span>

                    </div>

                    <p>
                        ${escapeHTML(message.message)}
                    </p>

                    <div class="message-meta">

                        <span>
                            To:
                            ${escapeHTML(message.receiver)}
                        </span>

                        <span>
                            ${formatTime(message.created_at)}
                        </span>

                    </div>

                </article>
            `;

        }).join("");

    } catch (error) {

        container.innerHTML = `
            <div class="empty">
                Unable to load messages.
            </div>
        `;

        console.error(
            "Message loading failed:",
            error
        );
    }
}


/* ============================================================
   SOS
   ============================================================ */

async function loadSOS() {

    const table =
        document.getElementById("sosTable");

    if (!table) {
        return;
    }

    try {

        const alerts =
            await fetchJSON(API.sos);

        const active =
            alerts.filter(
                alert => alert.status === "ACTIVE"
            ).length;

        setText(
            "activeSOS",
            active
        );

        setText(
            "sosCount",
            `${alerts.length} alerts`
        );

        if (alerts.length === 0) {

            table.innerHTML = `
                <tr>
                    <td colspan="8" class="empty">
                        No SOS alerts.
                    </td>
                </tr>
            `;

            return;
        }

        table.innerHTML = alerts.map(alert => {

            const location =
                `${Number(alert.latitude).toFixed(4)},
                 ${Number(alert.longitude).toFixed(4)}`;

            return `
                <tr>

                    <td>${escapeHTML(alert.id)}</td>

                    <td>
                        ${escapeHTML(alert.user_name)}
                    </td>

                    <td>
                        ${escapeHTML(alert.node_id)}
                    </td>

                    <td>
                        ${escapeHTML(alert.message)}
                    </td>

                    <td>${location}</td>

                    <td>
                        ${escapeHTML(alert.priority)}
                    </td>

                    <td>
                        ${escapeHTML(alert.status)}
                    </td>

                    <td>
                        ${formatTime(alert.created_at)}
                    </td>

                </tr>
            `;

        }).join("");

    } catch (error) {

        table.innerHTML = `
            <tr>
                <td colspan="8" class="empty">
                    Unable to load SOS alerts.
                </td>
            </tr>
        `;

        console.error(
            "SOS loading failed:",
            error
        );
    }
}


/* ============================================================
   LOCATIONS
   ============================================================ */

async function loadLocations() {

    const table =
        document.getElementById("locationTable");

    if (!table) {
        return;
    }

    try {

        const locations =
            await fetchJSON(API.locations);

        if (locations.length === 0) {

            table.innerHTML = `
                <tr>
                    <td colspan="7" class="empty">
                        No locations reported.
                    </td>
                </tr>
            `;

            return;
        }

        table.innerHTML = locations.map(location => {

            return `
                <tr>

                    <td>${escapeHTML(location.id)}</td>

                    <td>
                        ${escapeHTML(location.user_name)}
                    </td>

                    <td>
                        ${escapeHTML(location.node_id)}
                    </td>

                    <td>
                        ${Number(location.latitude).toFixed(6)}
                    </td>

                    <td>
                        ${Number(location.longitude).toFixed(6)}
                    </td>

                    <td>
                        ${Number(location.accuracy).toFixed(1)} m
                    </td>

                    <td>
                        ${formatTime(location.created_at)}
                    </td>

                </tr>
            `;

        }).join("");

    } catch (error) {

        table.innerHTML = `
            <tr>
                <td colspan="7" class="empty">
                    Unable to load locations.
                </td>
            </tr>
        `;

        console.error(
            "Location loading failed:",
            error
        );
    }
}


/* ============================================================
   RESOURCES
   ============================================================ */

async function loadResources() {

    const container =
        document.getElementById("resourceList");

    if (!container) {
        return;
    }

    try {

        const resources =
            await fetchJSON(API.resources);

        const pending =
            resources.filter(
                resource =>
                    resource.status === "PENDING"
            ).length;

        setText(
            "pendingResources",
            pending
        );

        if (resources.length === 0) {

            container.innerHTML = `
                <div class="empty">
                    No resource requests.
                </div>
            `;

            return;
        }

        container.innerHTML = resources.map(resource => {

            return `
                <article class="resource-item">

                    <div class="resource-header">

                        <strong>
                            ${escapeHTML(resource.resource)}
                        </strong>

                        <span class="status-badge">
                            ${escapeHTML(resource.status)}
                        </span>

                    </div>

                    <div class="resource-details">

                        <span>
                            Quantity:
                            ${escapeHTML(resource.quantity)}
                        </span>

                        <span>
                            Priority:
                            ${escapeHTML(resource.priority)}
                        </span>

                    </div>

                    <small>
                        ${escapeHTML(resource.user_name)}
                        ·
                        ${formatTime(resource.created_at)}
                    </small>

                </article>
            `;

        }).join("");

    } catch (error) {

        container.innerHTML = `
            <div class="empty">
                Unable to load resource requests.
            </div>
        `;

        console.error(
            "Resource loading failed:",
            error
        );
    }
}


/* ============================================================
   DASHBOARD REFRESH
   ============================================================ */

async function refreshDashboard() {

    await Promise.all([
        loadHealth(),
        loadNodes(),
        loadMessages(),
        loadSOS(),
        loadLocations(),
        loadResources()
    ]);

}


/* ============================================================
   STARTUP
   ============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        refreshDashboard();

        /*
         * Refresh automatically every 5 seconds.
         * This gives the dashboard near-live local updates
         * without requiring Internet connectivity.
         */

        setInterval(
            refreshDashboard,
            5000
        );

    }
);
