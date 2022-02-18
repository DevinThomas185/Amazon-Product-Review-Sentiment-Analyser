import React from 'react';
import logo from './logo.svg';
import './App.css';

import Button from 'react-bootstrap/Button'
import Card from 'react-bootstrap/Card'
import Col from 'react-bootstrap/Col'
import Container from 'react-bootstrap/Container'
import Form from 'react-bootstrap/Form'
import Row from 'react-bootstrap/Row'



class SearchBar extends React.Component {
  render() {
    return(
      <Form> {/*onSubmit needed*/}
        <Form.Group>
          <Container>
            <Row>
              <Col sm={10}>
                <Form.Control className='text' type='search' placeholder='Amazon Product URL'/> {/*onChange needed*/}
              </Col>
              <Col sm={2}>
                <Button type='submit' className="searchbutton" variant='outline-dark'>Search</Button>
              </Col>
            </Row>
          </Container>
        </Form.Group>
      </Form>
    )
  }
}

class App extends React.Component {
  render() {
    return (
      <Container>
        <Row>
          <Col>
            <h1>devin thomas</h1>
          </Col>
        </Row>
        <Row>
          <Col>
            <SearchBar />
          </Col>
        </Row>
      </Container>
    );
  }
}

export default App;
