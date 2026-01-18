# 📕 MASTER PAGE BLUEPRINT: Page 4 (The Miniature Gear Box)
**Version:** 3.5.2 (Production-Ready / Final Logic)
**Date:** January 12, 2026
**Theme:** Firefighter (Template Reference)
**Trim Size:** 8.5" x 8.5" (Bleed Compliant: 8.625" x 8.75")

---

## 1. DESIGN STRATEGY (Miniature Toy Kit)
* **Scale Logic:** 콘텐츠를 페이지 중앙의 **60% 영역**에 집중시켜 "장난감 세트"와 같은 심리적 안정감과 집중도를 부여함.
* **Margin Logic:** 상하좌우에 최소 **1.5인치 이상의 광활한 여백(Wide Margins)**을 확보하여 KDP 재단 안전성을 높이고 고급스러운 룩을 완성함.
* **Visual Style:** 모든 외곽선은 굵고 부드러운 **Rounded Corner(둥근 모서리)**를 사용하여 아동용 도서의 안전하고 귀여운 느낌을 강조함.

---

## 2. SPATIAL LAYOUT & ZONES
*이 데이터는 Python 제작 엔진(Agent Echo)의 좌표 및 마스킹 데이터로 사용됨*

### 🟥 ZONE 1: FIXED FRAME (고정 프레임)
* **Border Style:** 두꺼운 검은색 둥근 정사각형 테두리.
* **Shape:** 1:1 비율의 Perfect Square.
* **Red Guide:** 검은색 테두리 외곽선에 **Zero-Gap(무간격)**으로 밀착된 빨간색 실선.

### 🟩 ZONE 3: VARIABLE OBJECTS (가변 오브젝트)
* **Content:** 6개의 테마별 오브젝트 그리드.
* **Green Guide:** Zone 1의 곡률을 그대로 따라가는 **Rounded Green Solid Line**.
* **Constraint:** 오브젝트는 서로 중첩되거나 Green Zone의 경계를 벗어나지 않아야 함.

### 🟦 ZONE 2: DYNAMIC TEXT (가변 텍스트)
* **Vertical Positioning:** Zone 1 하단 경계선으로부터 **최소 0.5인치 이상의 수직 간격(White Space)**을 두고 하향 배치함.
* **Width Constraint:** 텍스트 블록의 전체 폭은 Zone 1(박스)의 가로 폭과 같거나 좁아야 함.
* **Blue Guide:** 텍스트를 타이트하게 감싸는 파란색 실선 박스.

---

## 3. PRODUCTION ASSETS (Verification Points)
* **Master Visual:** `ref_page4_01.png` (중앙 집중 레이아웃 및 하향 텍스트 확인용).
* **Structure Map:** `ref_page4_structure_example.png` (색상별 구역 분리 및 둥근 모서리 확인용).
* **Final Mask:** `ref_page4_layout_wireframe_kdp.png` (Zone 2, 3가 순수 화이트로 비워진 제작용 원본).

---

## 4. AUTOMATION LOGIC (For Agent Echo)
1. **Load:** `ref_page4_layout_wireframe_kdp.png`를 베이스 레이어로 로드.
2. **Object Filling:** Green Zone 내부에 테마별 고해상도 벡터 아이템 6개를 랜덤 그리드 배치.
3. **Text Injection:** Blue Zone의 중앙 좌표에 맞춰 테마 명칭("THEME GEAR")을 Titan One 폰트(Outlined)로 삽입.
4. **Final Export:** 모든 가이드 컬러(Red/Green/Blue) 및 레이블을 제거한 후 순수 Black & White 고해상도 PDF 출력.