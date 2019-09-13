import React from 'react';
import clsx from 'clsx';
import { HashRouter as Router, Route } from "react-router-dom";
import { withStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import Badge from '@material-ui/core/Badge';
import Container from '@material-ui/core/Container';
import Grid from '@material-ui/core/Grid';
import NotificationsIcon from '@material-ui/icons/Notifications';import './App.css';
import Dashboard from './Dashboard'
import Flows from "./Flows";
import Tasks from "./Tasks"

function Copyright() {
    return (
        <Typography variant="body2" color="textSecondary" align="center">
            {'Copyright © '}
            {new Date().getFullYear()}
        </Typography>
    );
}

const drawerWidth = 240;

const useStyles = theme => ({
    root: {
        display: 'flex',
    },
    toolbar: {
        paddingRight: 24, // keep right padding when drawer closed
    },
    toolbarIcon: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-end',
        padding: '0 8px',
        ...theme.mixins.toolbar,
    },
    appBar: {
        zIndex: theme.zIndex.drawer + 1,
        transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
        }),
    },
    appBarShift: {
        marginLeft: drawerWidth,
        width: `calc(100% - ${drawerWidth}px)`,
        transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
        }),
    },
    menuButton: {
        marginRight: 36,
    },
    menuButtonHidden: {
        display: 'none',
    },
    title: {
        flexGrow: 1,
    },
    drawerPaper: {
        position: 'relative',
        whiteSpace: 'nowrap',
        width: drawerWidth,
        transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
        }),
    },
    drawerPaperClose: {
        overflowX: 'hidden',
        transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
        }),
        width: theme.spacing(7),
        [theme.breakpoints.up('sm')]: {
            width: theme.spacing(9),
        },
    },
    appBarSpacer: theme.mixins.toolbar,
    content: {
        flexGrow: 1,
        height: '100vh',
        overflow: 'auto',
    },
    container: {
        paddingTop: theme.spacing(4),
        paddingBottom: theme.spacing(4),
    },
    paper: {
        padding: theme.spacing(2),
        display: 'flex',
        overflow: 'auto',
        flexDirection: 'column',
    },
    fixedHeight: {
        height: 240,
    },
});

class Login extends React.Component {
    state = {
        username: null,
        password: null
    };
    handleLogin = event => {
        event.preventDefault();
        localStorage.setItem('username', this.state.username);
        localStorage.setItem('password', this.state.password);
        this.props.closeLoginDialog(true)
    };
    handleInputChange = event => {
        if (event.target.name === 'username') {
            this.setState({username: event.target.value});
        } else if (event.target.name === 'password') {
            this.setState({password: event.target.value});
        }
    };

    render = () => {
        return (
        <div className={this.props.style.root}>
            <div className="Login">
                <form onSubmit={this.handleLogin}>
                    <div>Username: <input type="text" onChange={this.handleInputChange} name="username" placeholder="Username"></input></div>
                    <div>Password: <input type="password" onChange={this.handleInputChange} name="password" placeholder="Password"></input></div>
                    <button>Login</button>
                </form>
            </div>
        </div>
        )
    }
}

class App extends React.Component {
    state = {
        requireLogin: process.env.REACT_APP_REQUIRE_LOGIN,
        usernameExists: false
    };

    closeLoginDialog = (username_exists) => {
        this.setState({usernameExists: username_exists})
    };

    componentDidMount() {
        let has_credentials = localStorage.getItem('username');
        if (has_credentials) {
            this.setState({'usernameExists': true})
        }
    };

    render = () => {
        const classes = this.props.classes;
        if (this.state.requireLogin === 'true' &&  !this.state.usernameExists) {
            return (
                <Login style={classes} closeLoginDialog={this.closeLoginDialog} />
            )
        }
        return (
            <div className={classes.root}>
                <CssBaseline />
                <AppBar position="absolute" className={clsx(classes.appBar)}>
                    <Toolbar className={classes.toolbar}>
                        <Typography component="h1" variant="h6" color="inherit" noWrap className={classes.title}>
                            <a href="/" className="headerText">Airduct</a>
                        </Typography>
                        <IconButton color="inherit">
                            <Badge badgeContent={0} color="secondary">
                                <NotificationsIcon />
                            </Badge>
                        </IconButton>
                    </Toolbar>
                </AppBar>
                <main className={classes.content}>
                    <div className={classes.appBarSpacer} />
                    <Container maxWidth="lg" className={classes.container}>
                        <Grid container spacing={3}>
                            <Grid item xs={12}>
                                <Router>
                                    <Route path="/" exact component={() => <Dashboard style={classes} />} />
                                    <Route path="/flows/:schedule_name" component={props => <Flows {...props} style={classes}/>} />
                                    <Route path="/tasks/:flow_id" component={props => <Tasks  {...props} style={classes}/>} />
                                </Router>
                            </Grid>
                        </Grid>
                    </Container>
                    <Copyright />
                </main>
            </div>
        )
    };
}

export default withStyles(useStyles)(App);
