import streamlit as st
import pandas as pd

# --- 1. Page Config & CSS Injection ---
st.set_page_config(layout="wide", page_title="Grade Calculator")

st.markdown("""
<style>
    /* Main container padding adjustment */
    .block-container {
        padding: 2rem 5rem !important;
    }

    /* Fix Navigation Buttons: Ensure text is centered and not cut off */
    .stButton > button {
        height: auto !important;
        min-height: 42px !important; 
        padding: 6px 20px !important;
        line-height: 1.2 !important; 
        font-size: 16px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Card Design: Maximized font and icons */
    [data-testid="stElementContainer"]:has(#card-mark) + [data-testid="stElementContainer"] button,
    [data-testid="stElementContainer"]:has(#add-mark) + [data-testid="stElementContainer"] button {
        height: 250px !important;      
        min-height: 200px !important;
        background-color: #f8f9fa !important;
        border: 1px solid #e6e9ef !important;
        border-radius: 20px !important;
        display: flex !important;
        flex-direction: column !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
    }

    /* Font size set to 32px */
    [data-testid="stElementContainer"]:has(#card-mark) + [data-testid="stElementContainer"] button div p,
    [data-testid="stElementContainer"]:has(#add-mark) + [data-testid="stElementContainer"] button div p {
        white-space: pre-wrap !important;
        line-height: 1.1 !important;
        text-align: center !important;
        font-size: 32px !important;    
        font-weight: 800 !important;   
        margin: 0 !important;
    }

    /* Hover Effects */
    [data-testid="stElementContainer"]:has(#card-mark) + [data-testid="stElementContainer"] button:hover,
    [data-testid="stElementContainer"]:has(#add-mark) + [data-testid="stElementContainer"] button:hover {
        transform: translateY(-5px) !important;
        border-color: #007bff !important;
        background-color: #ffffff !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
    }

    /* Dashed style for "Add" buttons */
    [data-testid="stElementContainer"]:has(#add-mark) + [data-testid="stElementContainer"] button {
        border: 2px dashed #007bff !important;
        background-color: #f0f7ff !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. Core Logic Functions ---

def build_tree(df, semester, course):
    mask = (df['Semester'] == semester) & (df['Course'] == course)
    course_df = df[mask]
    tree = {}
    for _, row in course_df.iterrows():
        path_str = str(row['Path'])
        if path_str == "None" or not path_str or path_str == 'nan': continue
        parts = path_str.split('/')
        curr = tree
        for i, p in enumerate(parts):
            if p not in curr:
                if i == len(parts) - 1:
                    curr[p] = {"weight": float(row['Weight']), "grade": float(row['Grade']), "is_leaf": True}
                else:
                    curr[p] = {"sub_items": {}, "weight": 0.0, "grade": 0.0, "is_leaf": False}
            if not curr[p].get("is_leaf"): curr = curr[p]["sub_items"]
    return tree

def flatten_tree(tree, sem, course, path=""):
    rows = []
    if not tree:
        return [{"Semester": sem, "Course": course, "Path": None, "Weight": 0, "Grade": 0}]
    for n, info in tree.items():
        p = f"{path}/{n}" if path else n
        if info.get("is_leaf"):
            rows.append({"Semester": sem, "Course": course, "Path": p, "Weight": info['weight'], "Grade": info['grade']})
        elif "sub_items" in info:
            rows.extend(flatten_tree(info["sub_items"], sem, course, p))
    return rows

def calculate_totals(node_items):
    """
    Flat Calculation Logic:
    Categories act as containers and do not multiply weights.
    All sub-item weights are relative to the 100% course total.
    """
    total_contribution = 0.0
    for name, info in node_items.items():
        if info.get("is_leaf"):
            # Leaf node: Grade * (Weight/100)
            contribution = info["grade"] * (info["weight"] / 100.0)
            total_contribution += contribution
        else:
            # Category node: Summarize sub-item contributions
            sub_total_contribution = calculate_totals(info.get("sub_items", {}))
            info["grade"] = sub_total_contribution # Store for UI display
            total_contribution += sub_total_contribution
    return total_contribution

# --- 3. UI Components ---

@st.dialog("🚀 Initialization")
def init_modal():
    st.write("Welcome! How would you like to start using the Grade Calculator?")
    uploaded = st.file_uploader("Import previous CSV file", type="csv")
    if uploaded:
        st.session_state.db = pd.read_csv(uploaded)
        st.session_state.initialized = True
        st.rerun()
    st.divider()
    if st.button("✨ Start from Scratch", use_container_width=True):
        st.session_state.initialized = True
        st.rerun()

@st.dialog("✨ Add New Term")
def add_semester_dialog():
    st.write("Please enter the name of the new term:")
    name = st.text_input("Term Name", placeholder="e.g., 1B")
    if st.button("Create", use_container_width=True):
        if name:
            new_row = pd.DataFrame([{"Semester": name, "Course": None, "Path": None, "Weight": 0, "Grade": 0}])
            st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)
            st.session_state.sel_sem = name
            st.rerun()

@st.dialog("📘 Add New Course")
def add_course_dialog(current_sem):
    st.write(f"Adding new course for term: **{current_sem}**")
    name = st.text_input("Course Name", placeholder="e.g., CS136")
    if st.button("Create", use_container_width=True):
        if name:
            new_row = pd.DataFrame([{"Semester": current_sem, "Course": name, "Path": None, "Weight": 0, "Grade": 0}])
            st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)
            if 'current_tree' in st.session_state: del st.session_state.current_tree
            st.session_state.sel_course = name
            st.rerun()

def card_button(label, is_add=False, key=None):
    mark_id = "add-mark" if is_add else "card-mark"
    st.markdown(f'<span id="{mark_id}"></span>', unsafe_allow_html=True)
    icon = "➕" if is_add else "📂"
    return st.button(f"{icon}\n{label}", key=key, use_container_width=True)

def render_breakdown_editor(items, parent_key="root"):
    """Recursive editor for components, weights, and scores"""
    st.markdown(f"**➕ Add Item to this Level**")
    t_cols = st.columns([3, 1, 1, 0.5])
    new_n = t_cols[0].text_input("Item Name", key=f"in_new_{parent_key}", label_visibility="collapsed", placeholder="Enter name (e.g., Assignment 1)")
    
    if t_cols[1].button("➕ Scored Item", key=f"btn_leaf_{parent_key}", use_container_width=True):
        if new_n:
            items[new_n] = {"weight": 0.0, "grade": 0.0, "is_leaf": True}
            st.rerun()
    if t_cols[2].button("📂 Sub-category", key=f"btn_sub_{parent_key}", use_container_width=True):
        if new_n:
            items[new_n] = {"sub_items": {}, "weight": 0.0, "grade": 0.0, "is_leaf": False}
            st.rerun()
    st.divider()

    if items:
        h_cols = st.columns([3, 2, 2, 0.5])
        h_cols[0].caption("Component / Activity")
        h_cols[1].caption("Weight (%) - Relative to Course Total")
        h_cols[2].caption("Actual Score")

    to_delete = []
    temp_items = list(items.items())
    for i, (name, info) in enumerate(temp_items):
        stable_key = f"{parent_key}_row_{i}"
        
        if not info.get("is_leaf"):
            with st.expander(f"📂 Category: {name} (Contribution: {info.get('grade', 0):.2f})", expanded=True):
                if st.button("🗑️ Delete Category", key=f"del_cat_{stable_key}"):
                    to_delete.append(name)
                render_breakdown_editor(info["sub_items"], stable_key)
        else:
            cols = st.columns([3, 2, 2, 0.5])
            with cols[0]:
                new_val = st.text_input("Name", value=name, key=f"name_{stable_key}", label_visibility="collapsed")
                if new_val != name:
                    items[new_val] = items.pop(name); st.rerun()
            with cols[1]:
                info['weight'] = st.number_input("W", value=float(info['weight']), key=f"w_{stable_key}", label_visibility="collapsed")
            with cols[2]:
                info['grade'] = st.number_input("G", value=float(info['grade']), key=f"g_{stable_key}", label_visibility="collapsed")
            with cols[3]:
                if st.button("🗑️", key=f"del_{stable_key}"): to_delete.append(name); st.rerun()

    for n in to_delete:
        if n in items: del items[n]
    if to_delete: st.rerun()

# --- 4. Main Program Flow ---

def main():
    if 'db' not in st.session_state:
        st.session_state.db = pd.DataFrame(columns=["Semester", "Course", "Path", "Weight", "Grade"])
    
    if 'initialized' not in st.session_state:
        init_modal()
        return

    # A. Term List
    if not st.session_state.get('sel_sem'):
        st.title("📅 Select Term")
        sems = sorted([s for s in st.session_state.db['Semester'].unique() if pd.notna(s)])
        cols = st.columns(4)
        for i, sem in enumerate(sems):
            with cols[i % 4]:
                if card_button(sem, key=f"s_{sem}"):
                    st.session_state.sel_sem = sem
                    st.rerun()
        with cols[len(sems) % 4]:
            if card_button("Add Term", is_add=True, key="add_sem"):
                add_semester_dialog()
        return

    # B. Course List
    if st.session_state.sel_sem and not st.session_state.get('sel_course'):
        if st.button("⬅️ Back to Term Selection"):
            st.session_state.sel_sem = None
            if 'current_tree' in st.session_state: del st.session_state.current_tree
            st.rerun()
            
        st.title(f"📘 {st.session_state.sel_sem} Course List")
        raw_c = st.session_state.db[st.session_state.db['Semester'] == st.session_state.sel_sem]['Course'].unique()
        courses = [c for c in raw_c if pd.notna(c) and str(c) != 'None']
        
        cols = st.columns(3)
        for i, c in enumerate(courses):
            with cols[i % 3]:
                if card_button(c, key=f"c_{c}"):
                    st.session_state.sel_course = c
                    st.rerun()
        with cols[len(courses) % 3]:
            if card_button("Add Course", is_add=True, key="add_course"):
                add_course_dialog(st.session_state.sel_sem)
        return

    # C. Editor
    if st.session_state.sel_course:
        if st.button("⬅️ Back to Course List"):
            st.session_state.sel_course = None
            if 'current_tree' in st.session_state: del st.session_state.current_tree
            st.rerun()
        
        st.title(f"📝 Edit Course: {st.session_state.sel_course}")
        
        if 'current_tree' not in st.session_state:
            st.session_state.current_tree = build_tree(st.session_state.db, st.session_state.sel_sem, st.session_state.sel_course)
        
        f_score = calculate_totals(st.session_state.current_tree)
        render_breakdown_editor(st.session_state.current_tree)
        
        st.sidebar.metric("Estimated Total Grade", f"{f_score:.2f} / 100")

        if st.button("💾 Save & Update Data", type="primary", use_container_width=True):
            new_rows = flatten_tree(st.session_state.current_tree, st.session_state.sel_sem, st.session_state.sel_course)
            other_data = st.session_state.db[~((st.session_state.db['Semester'] == st.session_state.sel_sem) & (st.session_state.db['Course'] == st.session_state.sel_course))]
            st.session_state.db = pd.concat([other_data, pd.DataFrame(new_rows)], ignore_index=True)
            st.success("Data Synchronized!")
            
        st.sidebar.download_button("📥 Export Backup CSV", data=st.session_state.db.to_csv(index=False).encode('utf-8'), file_name="my_grades.csv")

if __name__ == "__main__":
    main()