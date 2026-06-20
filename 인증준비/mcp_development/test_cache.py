import sys
from easyeda_mcp_client import EasyEDAMCPClient

def main():
    client = EasyEDAMCPClient()
    if not client.connect():
        print("Failed to connect")
        sys.exit(1)
        
    js = """
    try {
        const libs = await eda.lib_LibrariesList.getAllLibrariesList();
        const sysUuid = await eda.lib_LibrariesList.getSystemLibraryUuid();
        const personalUuid = await eda.lib_LibrariesList.getPersonalLibraryUuid();
        const projectUuid = await eda.lib_LibrariesList.getProjectLibraryUuid();
        const favUuid = await eda.lib_LibrariesList.getFavoriteLibraryUuid();
        
        return { 
            success: true, 
            libs: libs ? libs.map(l => ({name: l.name, uuid: l.uuid, type: l.type})) : [], 
            sysUuid, 
            personalUuid, 
            projectUuid, 
            favUuid 
        };
    } catch(e) {
        return { success: false, error: e.message };
    }
    """
    res = client.execute_js(js)
    print("Result:", res)

if __name__ == "__main__":
    main()
