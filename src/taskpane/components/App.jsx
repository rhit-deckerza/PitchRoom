import * as React from "react";
import PropTypes from "prop-types";
import axios from "axios";
import Header from "./Header";
import HeroList from "./HeroList";
import TextInsertion from "./TextInsertion";
import { makeStyles } from "@fluentui/react-components";
import { Ribbon24Regular, LockOpen24Regular, DesignIdeas24Regular } from "@fluentui/react-icons";
import { insertText } from "../taskpane";

const useStyles = makeStyles({
  root: {
    minHeight: "100vh",
  },
});

const App = (props) => {
  const { title } = props;
  const [emailBody, setEmailBody] = React.useState(""); // State to store the email body
  const [result, setResult] = React.useState(null); // State to store the result from the backend

  // eslint-disable-next-line no-undef
  const item = Office.context.mailbox.item;

  // Use effect to handle the async body fetch
  React.useEffect(() => {
    if (item) {
      item.body.getAsync("text", (result) => {
        if (result.status === Office.AsyncResultStatus.Succeeded) {
          const body = result.value; // Get the body content
          setEmailBody(body); // Update state with the body content
          handleSubmit(body); // Send the email content to the Flask backend
        } else {
          console.error("Failed to fetch email body:", result.error);
        }
      });
    }
  }, [item]); // Run this effect when the item changes

  const handleSubmit = async (emailText) => {
    if (emailText.trim()) {
      try {
        const response = await axios.post("http://localhost:5000/process_pitch", {
          email_text: emailText,
        });
        setResult(response.data); // Store the response from the backend
      } catch (error) {
        console.error("There was an error processing the pitch:", error);
      }
    } else {
      alert("Please provide the email pitch text.");
    }
  };

  // Accessing subject and sender
  const subject = item.subject;
  const sender = item.sender.emailAddress;

  const styles = useStyles();

  // List items updated when body content is available
  const listItems = [
    {
      icon: <Ribbon24Regular />,
      primaryText: "Subject: " + subject,
    },
    {
      icon: <LockOpen24Regular />,
      primaryText: "Sender: " + sender,
    },
    {
      icon: <DesignIdeas24Regular />,
      primaryText: "Body: " + emailBody, // Use the state for the body text
    },
  ];

  return (
    <div className={styles.root}>
      <Header logo="assets/logo-filled.png" title={title} message="Welcome" />
      <HeroList message="Discover what this add-in can do for you today!" items={listItems} />
      {/* <TextInsertion insertText={insertText} /> */}

      {result && (
        <div>
          <h2>Enriched Company Information</h2>
          <p>
            <strong>Founder Name:</strong> {result.founder_name}
          </p>
          <p>
            <strong>Company Name:</strong> {result.company_name}
          </p>
          <p>
            <strong>Founders:</strong> {result.founders}
          </p>
          <p>
            <strong>Website:</strong> {result.company_website}
          </p>
          <p>
            <strong>Description:</strong> {result.company_description}
          </p>
          <p>
            <strong>Team Size:</strong> {result.team_size}
          </p>
          <p>
            <strong>Customer Type:</strong> {result.customer_type}
          </p>
          <p>
            <strong>Location:</strong> {result.location}
          </p>
          <p>
            <strong>Funding Amount:</strong> {result.funding_amount}
          </p>
          <p>
            <strong>Product Description:</strong> {result.product_description}
          </p>
        </div>
      )}
    </div>
  );
};

App.propTypes = {
  title: PropTypes.string,
};

export default App;
