import React from 'react';
import './App.css';
import "bootswatch/dist/lux/bootstrap.min.css";

import Accordion from 'react-bootstrap/Accordion'
import Alert from 'react-bootstrap/Alert'
import Button from 'react-bootstrap/Button'
import Card from 'react-bootstrap/Card'
import CardGroup from 'react-bootstrap/CardGroup'
import Col from 'react-bootstrap/Col'
import Container from 'react-bootstrap/Container'
import Form from 'react-bootstrap/Form'
import ListGroup from 'react-bootstrap/ListGroup'
import Row from 'react-bootstrap/Row'
import Spinner from 'react-bootstrap/Spinner'

function AlertDismissible() {
  const [show, setShow] = React.useState(true);

  return (
    <>
      <Alert show={show} variant="dark">
        <Alert.Heading align="center">How to use this service</Alert.Heading>
        <p align="justify">
          Type the URL or Amazon Standard Identification Number (ASIN) of a
          product from Amazon.co.uk, choose and Analysis Method, then press the
          ANALYSE button to analyse the reviews for that product. The Analysis
          Method dropdown will allow you choose a method of analysing the
          reviews. Rule-Based will use set rules whilst Automatic uses machine
          learning to analyse the reviews. Rule-Based is the recommended method
          and is set as default. The system will provide you with analytical
          data to aid you in making a decision on purchasing the product.

          If the Force Analysis checkbox is filled, the system will override the
          initial method of searching a database for the previously computed
          results. Instead, it will re-analyse a product as if it had never been
          analysed before.
        </p>
        <hr />
        <div className="d-flex justify-content-end">
          <Button onClick={() => setShow(false)} variant="outline-dark">Close</Button>
        </div>
      </Alert>

      {!show && <Button variant="outline-dark" onClick={() => setShow(true)}>Instructions</Button>}
    </>
  );
}

class CalculatedInfoCard extends React.Component {
  render(){
    return(
      <Card>
        <Accordion.Toggle as={Card.Header} align="center" eventKey={this.props.number}>{this.props.title}</Accordion.Toggle>
        <Accordion.Collapse eventKey={this.props.number}>
          <Card.Body>{this.props.data}</Card.Body>
        </Accordion.Collapse>
      </Card>
    );
  }
}

class CalculatedInfo extends React.Component {
  render(){
    return(
      <Accordion>
        <CalculatedInfoCard title="Most Positive Review" data={this.props.results.most_positive} number="0"/>
        <CalculatedInfoCard title="Most Critical Review" data={this.props.results.most_critical} number="1"/>
        <CalculatedInfoCard title="Analysed Reviews" data={this.props.results.noreviews} number="2"/>
        <CalculatedInfoCard title="Average Calculated Rating" data={this.props.results.avg} number="3"/>
      </Accordion>
    );
  }
}

class ReviewCard extends React.Component {
  render(){
    return(
      <Card border={this.props.type}>
        <Card.Body align="center">
          <Card.Title>{this.props.title}</Card.Title>
          <Card.Text>{this.props.number}%</Card.Text>
        </Card.Body>
      </Card>
    );
  }
}

class ReviewStats extends React.Component {
  render(){
    return(
      <CardGroup>
        <ReviewCard type="success" title="Positive Reviews" number={this.props.results.pos_percent}/>
        <ReviewCard type="warning" title="Neutral Reviews" number={this.props.results.neu_percent}/>
        <ReviewCard type="danger" title="Negative Reviews" number={this.props.results.neg_percent}/>
      </CardGroup>
    );
  }
}

class Images extends React.Component {
  render(){
    if (this.props.image == null) return(<p></p>);
    return(
      <img className='d-block w-100' src={this.props.image} alt="Product"/>
    );
  }
}

class ExtractedInfo extends React.Component {
  render(){
    return(
      <Card>
        <ListGroup>
          <ListGroup.Item>Price: {this.props.results.price}</ListGroup.Item>
          <ListGroup.Item>Seller: {this.props.results.seller}</ListGroup.Item>
          <ListGroup.Item>Amazon Rating: {this.props.results.rating}</ListGroup.Item>
          <ListGroup.Item>Number of Ratings: {this.props.results.noratings}</ListGroup.Item>
          <ListGroup.Item>Number of Reviews: {this.props.results.noreviews}</ListGroup.Item>
          <ListGroup.Item>ASIN: {this.props.results.asin}</ListGroup.Item>
        </ListGroup>
      </Card>
    );
  }
}

class RightContent extends React.Component {
  render(){
    return(
      <Container>
        <Row>
          <Col>
            <ReviewStats results={this.props.results}/>
          </Col>
        </Row>
        <Row>
          <Col>
            <CalculatedInfo results={this.props.results}/>
          </Col>
        </Row>
      </Container>
    );
  }
}

class LeftContent extends React.Component {
  render(){
    return(
      <Container>
        <Row>
          <Col>
            <Images image={this.props.results.image}/>
          </Col>
        </Row>
        <Row>
          <Col>
            <ExtractedInfo results={this.props.results}/>
          </Col>
        </Row>
      </Container>
    );
  }
}

class ProductInformation extends React.Component {
  render() {
    return(
      <Row>
        <Col md={3}>
          <LeftContent results={this.props.results}/>
        </Col>
        <Col md={9}>
          <RightContent results={this.props.results}/>
        </Col>
      </Row>
    );
  }
}

class Loader extends React.Component {
  render(){
    if (this.props.loading) return(
      <Button type='submit' className="searchbutton" variant='outline-dark'>
      <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />
      Analyse
      </Button>
    );
    return(
      <Button type='submit' className="searchbutton" variant='outline-dark'>
      Analyse
      </Button>
    );
  }
}

class SearchArea extends React.Component {
  /* Set up new states and props */
  constructor(props){
    super(props)
    this.state = {
      asin: "",
      loading: false,
    }
    this.handleClick = this.handleClick.bind(this)
    this.updateInput = this.updateInput.bind(this)
  }

  handleClick(event){
    this.setState({loading: true})
    event.preventDefault()
    this.props.updateASIN(this.state.asin)
    fetch("/infoReturn/" + this.props.analysis_type + "/" + String(this.props.force_analyse) + "/" + this.props.asin)
    .then(res => res.json())
    .then(
      (result) => {
        this.props.updateResults(result)
        this.setState({loading: false})
      }
    )
  }

  updateInput(event){
    this.setState({
      asin: event.target.value
    })
  }

  render() {
    return(
      <Form onSubmit={this.handleClick}>
        <Form.Group>
          <Row>
            <Col sm={10}>
              <Form.Control className='text' type='search' placeholder='Amazon Product URL or ASIN' onChange={this.updateInput}/>
            </Col>
            <Col sm={2}>
              <Loader loading={this.state.loading}/>
            </Col>
          </Row>
        </Form.Group>
      </Form>
    );
  }
}

class AnalysisSelector extends React.Component {
  constructor(props){
    super(props)
    this.handleChange = this.handleChange.bind(this)
  }

  /* Function to update the Analysis type */
  handleChange(event){
    this.props.updateAnalysisType(event.target.value)
  }

  render() {
    return(
      <Form align="center">
        <Form.Group>
          <Form.Label>Analysis Method</Form.Label>
          <Form.Control as="select" onChange={this.handleChange}>
              <option value="0">Rule-Based</option>
              <option value="1">Automatic</option>
          </Form.Control>
        </Form.Group>
      </Form>
    );
  }
}

class ForceCheck extends React.Component {
  constructor(props){
    super(props)
    this.state = {
      force_analyse: false
    }
    this.updateForce = this.updateForce.bind(this)
  }

  updateForce(event){
    this.props.updateForceAnalysis(event.target.checked)
  }

  render(){
    return(
      <Form>
        <Form.Check type='checkbox' label='Force Analysis' defaultChecked={this.state.force_analyse} onChange={this.updateForce}/>
      </Form>
    );
  }
}

class App extends React.Component {
  /* Set up states and props */
  constructor(props){
    super(props)
    this.state = {
      asin: "",
      analysis_type: "0",
      force_analyse: false,
      results: []
    }
    this.updateASIN = this.updateASIN.bind(this)
    this.updateAnalysisType = this.updateAnalysisType.bind(this)
    this.updateForceAnalysis = this.updateForceAnalysis.bind(this)
    this.updateResults = this.updateResults.bind(this)
  }

  /* Function to update the ASIN/URL */
  updateASIN(asin){
    this.setState({
      asin: asin,
    })
  }

  /* Function to update the Analysis type */
  updateAnalysisType(analysis_type){
    this.setState({
      analysis_type: analysis_type,
    })
  }

  /* Function to update the Force Analysis */
  updateForceAnalysis(force_analyse){
    this.setState({
      force_analyse: force_analyse,
    })
  }

  /* Function to update the results of the API request */
  updateResults(results){
    this.setState({
      results: results,
    })
  }

  render() {
    return(
      <Container>
        <Row>  {/* Title row division */}
          <Col>
            <h1 align="center">Amazon Product Review Sentiment Analyser</h1>
            <h5 align="center">Created by <i>Devin Thomas</i></h5>
            <h6 align="center">Data sourced from <i>Amazon</i></h6>
          </Col>
        </Row>
        <Row> {/* SearchArea row division */}
          <Col>
            <SearchArea updateASIN={this.updateASIN} updateResults={this.updateResults} asin={this.state.asin} analysis_type={this.state.analysis_type} force_analyse={this.state.force_analyse}/>
          </Col>
        </Row>
        <Row> {/* Analysis Type row division */}
          <Col>
            <AnalysisSelector updateAnalysisType={this.updateAnalysisType}/>
            </Col>
        </Row>
        <Row>  {/* Instructions row division */}
          <Col sm={10}>
            <AlertDismissible/>
          </Col>
          <Col sm={2}>
            <ForceCheck updateForceAnalysis={this.updateForceAnalysis}/>
          </Col>
        </Row>
        <Row>  {/* Product name row division */}
          <Col>
            <h2 placeholder="Product Name">{this.state.results.name}</h2>
          </Col>
        </Row>
        <Row>  {/* Outcome row division */}
          <Col>
            {this.state.results.outcome === "buy" && <h3 style={{color:'#5CB85C'}}>BUY</h3>}
            {this.state.results.outcome === "neutral" && <h3 style={{color:'#F0AD4E'}}>UNSURE</h3>}
            {this.state.results.outcome === "nobuy" && <h3 style={{color:'#D9534F'}}><b>DON'T BUY</b></h3>}
            {this.state.results.outcome === "error" && <h3 style={{color:'#000000'}}><b>ERROR</b></h3>}
          </Col>
          <Col>
            <h5>As of: {this.state.results.date_full}</h5>
          </Col>
        </Row>
        <Row> {/* ProductInformation row division */}
          <Col>
            <ProductInformation results={this.state.results} />
          </Col>
        </Row>
      </Container>
    );
  }
}

export default App;
