from zoneinfo import ZoneInfo

def format_datetime_local(utc_dt):
    if not utc_dt:
        return ""
    
    local_tz=ZoneInfo("America/Sao_Paulo")

    local_dt = utc_dt.astimezone(local_tz)

    return local_dt.strftime('%d/%m/%Y %H:%M')