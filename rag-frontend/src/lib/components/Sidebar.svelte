<script>
    import {Nav, NavbarBrand, NavItem, NavLink} from "@sveltestrap/sveltestrap";
    import { page } from "$app/state";
    import {getRoles} from "$lib/auth/keycloak.js";

    function active(path) {
        return page.url.pathname === path;
    }

</script>

<div class="sidebar-shell">
    <Nav vertical pills>
        <!-- Mettere un header con spazio fino al livello della navbar-->

        <div class="sidebar-section-title">Conversations</div>
        <NavItem>
            <NavLink class="nav-link" href="/app" active={active("/app")}>
                Chat
            </NavLink>
        </NavItem>

        <NavItem>
            <NavLink class="nav-link" href="/app/saved-conversations" active={active("/app/saved-conversations")}>
                Saved conversations
            </NavLink>
        </NavItem>

        {#if getRoles().includes("ADMIN")}
            <div class="sidebar-section-title">Admin area</div>
            <NavItem>
                <NavLink class="nav-link" href="/app/admin/docs" active={active("/app/admin/docs")}>
                    Documents
                </NavLink>
            </NavItem>

            <NavItem>
                <NavLink class="nav-link" href="/app/admin/logs" active={active("/app/admin/logs")}>
                    Logs
                </NavLink>
            </NavItem>

        {/if}

    </Nav>


</div>

<style>
    .sidebar-shell {
        display: flex;
        width: 280px;
        height: 100%;
        flex-direction: column;
        padding: 1rem;
    }

    .sidebar-section-title {
        margin: 0.75rem 0 0.35rem;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #6c757d;
    }
    :global(.sidebar-shell .nav-link) {
        padding: 0.35rem 0.6rem;
        font-size: 0.9rem;
        border-radius: 0.45rem;
    }
</style>
