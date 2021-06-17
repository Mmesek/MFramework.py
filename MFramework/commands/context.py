from MFramework import onDispatch

@onDispatch(event="message_create", priority=1)
async def check_context(self, data) -> bool:
    return False