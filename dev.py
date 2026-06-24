def setup_frontend():
    if SKIP_FRONTEND:
        print()
        print(">>> Skipping frontend (--no-frontend)")
        return False

    if not FRONTEND_DIR.is_dir():
        print()
        print(">>> frontend/ not found, skipping frontend")
        return False

    npm = shutil.which("npm.cmd" if sys.platform == "win32" else "npm")

    if npm is None:
        print()
        print(">>> npm not in PATH. Install Node.js 18+ then re-run.")
        print("    https://nodejs.org/")
        return False

    print("  npm:    " + npm)

    if not (FRONTEND_DIR / "node_modules").exists():
        step("npm install")
        run(
            [npm, "install", "--no-audit", "--no-fund"],
            cwd=str(FRONTEND_DIR),
            check=True,
        )

    step("npm run build")
    run(
        [npm, "run", "build"],
        cwd=str(FRONTEND_DIR),
        check=True,
    )

    build_out = FRONTEND_DIR / "dist"

    if not build_out.exists():
        print("  WARNING: expected build output at " + str(build_out))
        return False

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)

    shutil.copytree(build_out, DIST_DIR)
    print("  Bundle copied to " + str(DIST_DIR))
    return True