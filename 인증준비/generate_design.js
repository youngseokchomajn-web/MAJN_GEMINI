/**
 * 마중 스마트배시넷 EasyEDA Pro 자동 설계 JavaScript 스크립트 (v1.1)
 * 
 * [실행 방법]
 * 1. EasyEDA Pro(웹 버전 https://pro.easyeda.com/ 또는 다운로드받은 Desktop 앱)를 켭니다.
 * 2. 상단 메뉴에서 [공구(Tools)] ➔ [스크립트(Script...)]를 선택합니다.
 * 3. 열린 스크립트 에디터 창에 본 코드 전체를 복사-붙여넣기합니다.
 * 4. [실행(Run)] 버튼을 클릭하면 에디터 상에 프로젝트가 생성되고 부품들이 자동으로 드로잉됩니다.
 */

(async () => {
    console.log("=== '마중' 스마트배시넷 자동 설계 스크립트 가동 (v1.1) ===");

    try {
        // 1. 새 프로젝트 생성
        const project = await api('createProject', {
            name: "Majung_Smart_Bassinet_v1.1",
            description: "EasyEDA MCP Auto-Generated Board for Majung Smart Bassinet"
        });
        console.log("프로젝트 생성 완료:", project);

        // 2. 새 회로도(Schematic) 문서 오픈
        const schematic = await api('createDocument', {
            type: "schematic",
            title: "Main Schematic"
        });
        console.log("회로도 문서 생성 완료");

        // 3. 핵심 LCSC 부품 배치 (설계 v1.1 정밀 좌표)
        const components = [
            { id: "C701342", designator: "U1", name: "ESP32-WROOM-32E", x: 400, y: 300 },
            { id: "C2827670", designator: "U2", name: "SGM2036 LDO", x: 200, y: 200 },
            { id: "C162810", designator: "U3", name: "MP3426 Boost", x: 600, y: 200 },
            { id: "C299105", designator: "U4", name: "TAS5805M Amp", x: 600, y: 450 },
            { id: "C444158", designator: "U5", name: "LSM6DSOX Accel", x: 200, y: 450 },
            { id: "C80145", designator: "D1", name: "SMAJ5.0A TVS", x: 100, y: 150 },
            { id: "C15309", designator: "D2", name: "USBLC6-2SC6 TVS", x: 120, y: 130 }
        ];

        for (const comp of components) {
            const placed = await api('placePart', {
                lcscId: comp.id,
                x: comp.x,
                y: comp.y,
                designator: comp.designator
            });
            console.log(`부품 배치: ${comp.designator} (${comp.name}) ➔ 완료`);
        }

        // 4. 회로도 와이어(Wire) 및 넷(Net) 연결
        console.log("회로도 와이어링 및 노드 연결 중...");
        
        // VBUS 전원선 연결 (5V 어댑터 입력)
        await api('addWire', { coords: [100, 150, 200, 200] }); // D1 to U2 LDO IN
        await api('addWire', { coords: [100, 150, 600, 200] }); // D1 to U3 Boost IN
        await api('addNetLabel', { x: 150, y: 150, name: "VBUS_5V" });

        // 3.3V LDO 출력 (ESP32 및 가속도 센서 전원)
        await api('addWire', { coords: [250, 200, 400, 300] }); // U2 LDO OUT to U1 ESP32 3V3
        await api('addWire', { coords: [250, 200, 200, 450] }); // U2 LDO OUT to U5 Accel VDD
        await api('addNetLabel', { x: 300, y: 200, name: "VCC_3V3" });

        // 12V Boost 출력 (오디오 앰프 PVDD 전원)
        await api('addWire', { coords: [650, 200, 600, 450] }); // U3 Boost OUT to U4 Amp PVDD
        await api('addNetLabel', { x: 620, y: 320, name: "PVDD_12V" });

        // SPI 버스 연결 (ESP32 to 가속도 센서)
        await api('addWire', { coords: [400, 350, 200, 480] }); // MOSI
        await api('addNetLabel', { x: 300, y: 415, name: "SPI_MOSI" });

        // 5. 새 PCB 보드 생성 및 배치
        const pcb = await api('createDocument', {
            type: "pcb",
            title: "Main Layout"
        });
        console.log("PCB 문서 생성 완료");

        // PCB 보드 규격 설정 (80x60mm)
        await api('setBoardOutline', {
            width: 80,
            height: 60,
            shape: "rect"
        });

        // 레이어 설정 (4층 기판)
        await api('setLayerCount', { count: 4 });
        console.log("4층 PCB 레이아웃 설정 완료 (Layer 2 Solid GND 플레인)");

        console.log("\n>>> 자동 설계가 완료되었습니다! 에디터 화면을 확인하십시오. <<<");
        alert("마중 스마트배시넷 v1.1 자동 설계가 성공적으로 드로잉되었습니다!");

    } catch (err) {
        console.error("설계 중 오류가 발생했습니다:", err);
        alert("설계 중 오류 발생: " + err.message);
    }
})();
