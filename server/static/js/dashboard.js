/* ============================================================
   OFFLINE COMM SYSTEM
   Rescue Dashboard JavaScript
   ============================================================ */


/* ============================================================
   GLOBAL
   ============================================================ */

const REFRESH_INTERVAL = 5000;


/* ============================================================
   UTILITY FUNCTIONS
   ============================================================ */

function escapeHTML(value) {

    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function formatTime(value) {

    if (!value) {
        return "-";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString();
}


function formatCoordinate(value) {

    if (value === null || value === undefined) {
        return "-";
    }

    return Number(value).toFixed(5);
}


function priorityBadge(priority) {

    const value = String(priority || "NORMAL").toUpperCase();

    let className = "badge-medium";

    if (value === "HIGH" || value === "CRITICAL") {
        className = "badge-high";
    }

    if (value === "LOW") {
        className = "badge-low";
    }

    return `
        <span class="badge ${className}">
            ${escapeHTML(value)}
        </span>
    `;
}


function statusBadge(status) {

    const value = String(status || "UNKNOWN").toUpperCase();

    let className = "badge-offline";

    if (value === "ACTIVE" || value === "RECEIVED") {
        className = "badge-active";
    }

    if (
        value === "ONLINE" ||
        value === "RESOLVED" ||
        value === "COMPLETED"
    ) {
        className = "badge-online";
    }

    if (
        value === "PENDING" ||
        value === "PROCESSING"
    ) {
        className = "badge-pending";
    }

    return `
        <span class="badge ${className}">
            ${escapeHTML(value)}
        </span>
    `;
}


/* ============================================================
   API REQUEST
   ============================================================ */

async function fetchAPI(endpoint) {

    const response = await fetch(endpoint, {
        method: "GET",
        cache: "no-store"
    });

    if (!response.ok) {
        throw new Error(
            `HTTP ${response.status} - ${endpoint}`
        );
    }

    return await response.json();
}


/* ============================================================
   SERVER STATUS
   ============================================================ */

async function loadSystemStatus() {

    try {

        const data = await fetchAPI("/api/status");

        document.getElementById("activeSOS").textContent =
            data.active_sos;

        document.getElementById("onlineNodes").textContent =
            data.online_nodes;

        document.getElementById("totalNodes").textContent =
            data.total_nodes;

        document.getElementById("totalMessages").textContent =
            data.total_messages;

        document.getElementById("pendingResources").textContent =
            data.pending_resources;

        document.getElementById("serverStatus").textContent =
            "Server online";

        document.getElementById("sidebarServerStatus").textContent =
            "Operational";

        document.getElementById("serverDot").style.background =
            "#237a57";

        document.getElementById("sidebarServerDot").style.background =
            "#237a57";

        document.getElementById("lastUpdated").textContent =
            "Updated " + formatTime(data.last_updated);

    } catch (error) {

        console.error("System status error:", error);

        document.getElementById("serverStatus").textContent =
            "Server unavailable";

        document.getElementById("sidebarServerStatus").textContent =
            "Disconnected";

        document.getElementById("serverDot").style.background =
            "#c0392b";

        document.getElementById("sidebarServerDot").style.background =
            "#c0392b";
    }
}


/* ============================================================
   SOS
   ============================================================ */

async function loadSOS() {

    const table = document.getElementById("sosTable");

    try {

        const alerts = await fetchAPI("/api/sos");

        document.getElementById("sosCount").textContent =
            `${alerts.length} alert${alerts.length === 1 ? "" : "s"}`;

        if (alerts.length === 0) {

            table.innerHTML = `
                <tr>
                    <td colspan="8" class="empty">
                        No SOS alerts recorded.
                    </td>
                </tr>
            `;

            return;
        }


        table.innerHTML = alerts.map(alert => {

            const latitude =
                formatCoordinate(alert.latitude);

            const longitude =
                formatCoordinate(alert.longitude);

            return `
                <tr>

                    <td class="id-cell">
                        #${escapeHTML(alert.id)}
                    </td>

                    <td>
                        ${escapeHTML(alert.user_name || "Unknown")}
                    </td>

                    <td>
                        ${escapeHTML(alert.node_id || "-")}
                    </td>

                    <td>
                        ${escapeHTML(alert.message || "-")}
                    </td>

                    <td class="location-cell">
                        ${latitude},
                        ${longitude}
                    </td>

                    <td>
                        ${priorityBadge(alert.priority)}
                    </td>

                    <td>
                        ${statusBadge(alert.status)}
                    </td>

                    <td>
                        ${escapeHTML(
                            formatTime(alert.created_at)
                        )}
                    </td>

                </tr>
            `;

        }).join("");

    } catch (error) {

        console.error("SOS error:", error);

        table.innerHTML = `
            <tr>
                <td colspan="8" class="empty">
                    Unable to load SOS alerts.
                </td>
            </tr>
        `;
    }
}


/* ============================================================
   MESSAGES
   ============================================================ */

async function loadMessages() {

    const container =
        document.getElementById("messageList");

    try {

        const messages =
            await fetchAPI("/api/messages");

        if (messages.length === 0) {

            container.innerHTML = `
                <div class="loading">
                    No messages recorded.
                </div>
            `;

            return;
        }


        const recentMessages =
            messages.slice(0, 8);


        container.innerHTML =
            recentMessages.map(message => {

                return `
                    <div class="message-item">

                        <div class="message-top">

                            <span class="message-sender">
                                ${escapeHTML(
                                    message.sender || "Unknown"
                                )}
                            </span>

                            <span class="message-time">
                                ${escapeHTML(
                                    formatTime(
                                        message.created_at
                                    )
                                )}
                            </span>

                        </div>


                        <div class="message-body">
                            ${escapeHTML(
                                message.message || "-"
                            )}
                        </div>


                        <div class="message-meta">
                            ${escapeHTML(
                                message.node_id || "Unknown node"
                            )}
                            →
                            ${escapeHTML(
                                message.receiver || "Broadcast"
                            )}
                        </div>

                    </div>
                `;

            }).join("");

    } catch (error) {

        console.error("Message error:", error);

        container.innerHTML = `
            <div class="loading">
                Unable to load messages.
            </div>
        `;
    }
}


/* ============================================================
   RESOURCES
   ============================================================ */

async function loadResources() {

    const container =
        document.getElementById("resourceList");

    try {

        const resources =
            await fetchAPI("/api/resources");

        if (resources.length === 0) {

            container.innerHTML = `
                <div class="loading">
                    No resource requests recorded.
                </div>
            `;

            return;
        }


        const recentResources =
            resources.slice(0, 8);


        container.innerHTML =
            recentResources.map(resource => {

                return `
                    <div class="resource-item">

                        <div class="resource-top">

                            <span class="resource-name">
                                ${escapeHTML(
                                    resource.resource
                                )}
                                ×
                                ${escapeHTML(
                                    resource.quantity || 1
                                )}
                            </span>

                            <span class="resource-time">
                                ${escapeHTML(
                                    formatTime(
                                        resource.created_at
                                    )
                                )}
                            </span>

                        </div>


                        <div class="resource-meta">

                            ${escapeHTML(
                                resource.user_name || "Unknown"
                            )}

                            ·

                            ${escapeHTML(
                                resource.node_id || "Unknown node"
                            )}

                            ·

                            ${priorityBadge(
                                resource.priority
                            )}

                            &nbsp;

                            ${statusBadge(
                                resource.status
                            )}

                        </div>

                    </div>
                `;

            }).join("");

    } catch (error) {

        console.error("Resource error:", error);

        container.innerHTML = `
            <div class="loading">
                Unable to load resource requests.
            </div>
        `;
    }
}


/* ============================================================
   LOCATIONS
   ============================================================ */

async function loadLocations() {

    const table =
        document.getElementById("locationTable");

    try {

        const locations =
            await fetchAPI("/api/locations");

        if (locations.length === 0) {

            table.innerHTML = `
                <tr>
                    <td colspan="7" class="empty">
                        No locations recorded.
                    </td>
                </tr>
            `;

            return;
        }


        table.innerHTML =
            locations.map(location => {

                return `
                    <tr>

                        <td class="id-cell">
                            #${escapeHTML(location.id)}
                        </td>

                        <td>
                            ${escapeHTML(
                                location.user_name || "-"
                            )}
                        </td>

                        <td>
                            ${escapeHTML(
                                location.node_id || "-"
                            )}
                        </td>

                        <td class="location-cell">
                            ${formatCoordinate(
                                location.latitude
                            )}
                        </td>

                        <td class="location-cell">
                            ${formatCoordinate(
                                location.longitude
                            )}
                        </td>

                        <td>
                            ${
                                location.accuracy !== null &&
                                location.accuracy !== undefined
                                    ? escapeHTML(
                                        location.accuracy
                                    ) + " m"
                                    : "-"
                            }
                        </td>

                        <td>
                            ${escapeHTML(
                                formatTime(
                                    location.created_at
                                )
                            )}
                        </td>

                    </tr>
                `;

            }).join("");

    } catch (error) {

        console.error("Location error:", error);

        table.innerHTML = `
            <tr>
                <td colspan="7" class="empty">
                    Unable to load locations.
                </td>
            </tr>
        `;
    }
}


/* ============================================================
   ESP32 NODES
   ============================================================ */

async function loadNodes() {

    const container =
        document.getElementById("nodeGrid");

    try {

        const nodes =
            await fetchAPI("/api/nodes");

        if (nodes.length === 0) {

            container.innerHTML = `
                <div class="loading">
                    No ESP32 nodes registered.
                </div>
            `;

            return;
        }


        container.innerHTML =
            nodes.map(node => {

                const online =
                    String(node.status || "")
                        .toUpperCase() === "ONLINE";


                return `
                    <div class="node-card">

                        <div class="node-header">

                            <div>

                                <div class="node-name">
                                    ${escapeHTML(
                                        node.node_name ||
                                        node.node_id
                                    )}
                                </div>

                                <div class="node-id">
                                    ${escapeHTML(
                                        node.node_id
                                    )}
                                </div>

                            </div>


                            <div class="node-status">

                                <span
                                    class="node-status-dot ${
                                        online
                                            ? "online"
                                            : ""
                                    }"
                                ></span>

                                <span class="node-status-text">
                                    ${escapeHTML(
                                        node.status ||
                                        "UNKNOWN"
                                    )}
                                </span>

                            </div>

                        </div>


                        <div class="node-data">

                            <div>

                                <div class="node-data-label">
                                    ROLE
                                </div>

                                <div class="node-data-value">
                                    ${escapeHTML(
                                        node.role || "-"
                                    )}
                                </div>

                            </div>


                            <div>

                                <div class="node-data-label">
                                    BATTERY
                                </div>

                                <div class="node-data-value">
                                    ${
                                        node.battery !== null &&
                                        node.battery !== undefined
                                            ? escapeHTML(
                                                node.battery
                                            ) + "%"
                                            : "-"
                                    }
                                </div>

                            </div>


                            <div>

                                <div class="node-data-label">
                                    SIGNAL
                                </div>

                                <div class="node-data-value">
                                    ${
                                        node.signal_strength !== null &&
                                        node.signal_strength !== undefined
                                            ? escapeHTML(
                                                node.signal_strength
                                            ) + " dBm"
                                            : "-"
                                    }
                                </div>

                            </div>


                            <div>

                                <div class="node-data-label">
                                    LAST SEEN
                                </div>

                                <div class="node-data-value">
                                    ${escapeHTML(
                                        formatTime(
                                            node.last_seen
                                        )
                                    )}
                                </div>

                            </div>

                        </div>

                    </div>
                `;

            }).join("");

    } catch (error) {

        console.error("Node error:", error);

        container.innerHTML = `
            <div class="loading">
                Unable to load ESP32 nodes.
            </div>
        `;
    }
}


/* ============================================================
   COMPLETE DASHBOARD REFRESH
   ============================================================ */

async function refreshDashboard() {

    await Promise.all([
        loadSystemStatus(),
        loadSOS(),
        loadMessages(),
        loadResources(),
        loadLocations(),
        loadNodes()
    ]);
}


/* ============================================================
   NAVIGATION
   ============================================================ */

function setupNavigation() {

    const navItems =
        document.querySelectorAll(".nav-item");

    navItems.forEach(item => {

        item.addEventListener("click", () => {

            navItems.forEach(nav => {
                nav.classList.remove("active");
            });

            item.classList.add("active");

        });

    });
}


/* ============================================================
   INITIALIZATION
   ============================================================ */

document.addEventListener("DOMContentLoaded", () => {

    setupNavigation();

    refreshDashboard();

    setInterval(
        refreshDashboard,
        REFRESH_INTERVAL
    );

});
