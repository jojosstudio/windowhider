#include <windows.h>

#define WDA_EXCLUDEFROMCAPTURE 0x00000011
#define WDA_NONE 0x00000000

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    return TRUE;
}

__declspec(dllexport) void SetExcludeCapture(DWORD flag) {
    DWORD pid = GetCurrentProcessId();
    HWND hwnd = NULL;
    while ((hwnd = FindWindowEx(NULL, hwnd, NULL, NULL)) != NULL) {
        DWORD windowPid = 0;
        GetWindowThreadProcessId(hwnd, &windowPid);
        if (windowPid == pid && IsWindowVisible(hwnd)) {
            SetWindowDisplayAffinity(hwnd, flag);
        }
    }
}
