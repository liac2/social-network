
function pagination (data, type) {
    let pagination_div = window.profile_view.querySelector('#pagination');
    if (type === 'all' || type === 'following') {
        pagination_div = window.view.querySelector('#pagination');
    }
    if (pagination_div === null) {
        pagination_div = document.createElement('div');
        pagination_div.id = 'pagination';
        window.type = type;
    }
    if (type === 'profile') {
        window.profile_view.append(pagination_div);
        // console.log('div');
        // console.log(window.profile_view);
    } else {
        window.view.append(pagination_div);
    }
    
    ReactDOM.render(<Pagination d={data}/>, pagination_div);
}

function Pagination (props) { 

    const [state, setState] = React.useState(props.d);

    return (
        <nav className="mt-3" aria-label="pagination">
        <ul className="pagination">
            <Button name='Previous' active={state.has_previous} num={state.current - 1} />
            
            <Pages num_pages={state.num_pages} current={state.current} />

            <Button name='Next' active={state.has_next} num={state.current + 1} />
        </ul>
        </nav>
    );
}

function Pages (props) {
    let rows = [];
    for (let i of props.num_pages) {
        rows.push(<Page active={props.current === i} num={i} />);
    }
    return (
        rows
    );
}

function Page (props) {
    if (props.active) {
        return (
            <li className='page-item active' aria-current="page">
                <span className="page-link">
                    {props.num}
                </span>
            </li>   
        );
    }
    return (
        <li className='page-item'>
        <a className="page-link" onClick={loadPage} href={props.num} data-page={props.num}>
            {props.num}
        </a>
        </li>    
    );
}

function loadPage (event) {
    event.preventDefault();

    // Get page that should get loaded
    let page = event.target.dataset.page;

    // Load function in order to load page
    if (window.type === undefined) { 
        console.log('error: window.type is undefined')
    }   
    else if (window.type === 'profile') {
        profile(window.type, page);
    } else {
        all_posts(window.type, page);
    }
}

function Button (props) {
    if (!props.active) {
        return (
            <li className="page-item"><span className={props.active ? "page-link" : "disabled page-link"} href={props.active ? props.num : undefined}>
            {props.name}
        </span></li>
        );
    }
    return (
        <li className="page-item"><a className="page-link" onClick={loadPage} data-page={props.num} href={props.num}>
            {props.name}
        </a></li>
    );
}