def require_settings(ctx):
    settings_found = ctx.bot.db.settings.get(ctx.author.id, None)

    if not settings_found:
        # clean up - set internally within database method
        settings = ctx.bot.db.create_settings()
        settings_found = ctx.bot.db.settings[ctx.author.id] = settings
    return settings_found
