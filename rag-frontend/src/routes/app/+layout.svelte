<script>

import Sidebar from "$lib/components/Sidebar.svelte";
import {Button, Nav, Navbar, NavbarBrand, NavItem} from "@sveltestrap/sveltestrap";
import {isAuthenticated, login, logout} from "$lib/auth/keycloak.js";

let {children} = $props();
let sidebarOpen = $state(true);

</script>

<div class="app-shell">
    <aside class:collapsed={!sidebarOpen} class="app-sidebar">
        <Sidebar/>
    </aside>

    <section class="app-main">
        <header class="app-navbar-shell">
            <Navbar container={false} light expand="md" class="w-100">
                <div class="d-flex w-100 align-items-center gap-3 px-3">
                    <Button
                        color="secondary"
                        outline
                        size="sm"
                        type="button"
                        aria-label={sidebarOpen ? "Chiudi sidebar" : "Apri sidebar"}
                        onclick={() => sidebarOpen = !sidebarOpen}
                    >
                        {sidebarOpen ? "‹" : "☰"}
                    </Button>

                    <NavbarBrand href="/app">
                        <img src=/logo.png alt="Logo" height="40" class="me-2"/>
                        <span class="app-name">Unical Computer Science</span>
                    </NavbarBrand>

                    <Nav class="ms-auto">
                        <NavItem>
                            {#if !isAuthenticated()}
                                <Button color="primary" onclick={login}>Login</Button>
                            {:else}
                                <Button color="danger" onclick={logout}>Logout</Button>
                            {/if}
                        </NavItem>
                    </Nav>

                </div>
            </Navbar>
        </header>

        <main class="app-content">
            <div class="content-frame">
                {@render children()}
            </div>
        </main>
    </section>
</div>

<style>
    :global(body) {
        margin: 0;
        background: #f4f6f8;
    }

    .app-shell {
        display: flex;
        width: 100vw;
        height: 100vh;
        overflow: hidden;
        background: #f4f6f8;
        color: #1f2937;
    }

    .app-sidebar {
        width: 280px;
        flex: 0 0 280px;
        height: 100vh;
        overflow: hidden;
        background: #eef1f4;
        border-right: 1px solid #d9dee5;
        transition: width 0.2s ease, flex-basis 0.2s ease;
    }

    .app-sidebar.collapsed {
        width: 0;
        flex-basis: 0;
        border-right: 0;
    }

    .app-main {
        display: flex;
        min-width: 0;
        height: 100vh;
        flex: 1;
        flex-direction: column;
    }

    .app-navbar-shell {
        display: flex;
        align-items: center;
        height: 64px;
        flex: 0 0 64px;
        background: #ffffff;
        border-bottom: 1px solid #dfe4ea;
    }

    .app-name {
        font-size: 0.98rem;
        font-weight: 700;
        line-height: 1.2;
    }

    .app-content {
        flex: 1;
        min-height: 0;
        overflow: hidden;
        padding: 1rem;
    }

    .content-frame {
        display: flex;
        height: 100%;
        min-height: 0;
        flex-direction: column;
        margin: 0 auto;
        padding: 1.5rem;
        background: #ffffff;
        border: 1px solid #e1e7ef;
        border-radius: 12px;
        box-sizing: border-box;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.04);
    }
</style>
