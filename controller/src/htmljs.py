HTML_HEAD = '''<!DOCTYPE html>
<html>
  <head>
    <script>
        let ids = [];
        answers1 = [];
        answers2 = [];
        preScores = [];

      function getExampleValues() {
        fetch("/api/example")
          .then(response => response.json())
          .then(data => {
            // Populate the first column of edit fields with the values from the response
            ids = [];
            for (let i = 0; i < 5; i++) {
                ids.push(data[i].id);
                answers1.push(data[i].past);
                answers2.push(data[i].past_participle);
                preScores.push(data[i].score);
                document.getElementById(`example_${i}`).value = data[i].verb;
                if (data[i].past.includes("/")) {
                  document.getElementById("answer1_" + i).value = "/";
                }
                if (data[i].past_participle.includes("/")) {
                  document.getElementById("answer2_" + i).value = "/";
                }
            }
          });
      }

      async function submitForm() {
        // Collect the answers from the form
        let answers = [];
        for (let i = 0; i < 5; i++) {
          let answer1 = document.getElementById("answer1_" + i).value;
          let answer2 = document.getElementById("answer2_" + i).value;
          let id = ids[i];
          answers.push({ id, answer1, answer2 });
        }

        // Send the answers to the API
        let response = await fetch("/api/example/submit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(answers),
        });
        let data = await response.json();
        
        for (let i = 0; i < 5; i++) {
          sc = (data.scores[i] * 100);
          delta = sc-(preScores[i] * 100);
          sign = delta>0 ? "+" : "";
          document.getElementById(`example_${i}`).value += " " +sc.toFixed(1)+"% ("+sign+delta.toFixed(1)+"%)";
          // Block the edit fields
          document.getElementById("answer1_" + i).readOnly = true;
          document.getElementById("answer2_" + i).readOnly = true;
        }
        // Check the response for errors
        if (data.mistakes.length > 0) {
          for (let i = 0; i < data.mistakes.length; i++) {
            misId = data.mistakes[i];
            document.getElementById("row_" + misId).style.backgroundColor = "red";
            document.getElementById("answer1_" + misId).value += " (" + answers1[misId] + ")"; 
            document.getElementById("answer2_" + misId).value += " (" + answers2[misId] + ")"; 
          }
        }
        document.getElementById("submitButton").style.display = "none";
        document.getElementById("nextButton").style.display = "inline-block";
      }
      function next() {
        location.reload();
      }
    </script>
  </head>
'''
HTML_BODY = '''  <body onload="getExampleValues()">
    <form>
      <table>
        <tbody>
          {table_body}
        </tbody>
      </table>
      <button type="button" id="submitButton" onclick="submitForm()">Submit</button>
      <input type="button" value="Next" id="nextButton" style="display: none" onclick="next()">
    </form>
  </body>
</html>'''
HTML_BODY_ROW = '''<tr id="row_{ind}">
              <td>
                <input type="text" id="example_{ind}" disabled>
              </td>
              <td>
                <input type="text" id="answer1_{ind}">
              </td>
              <td>
                <input type="text" id="answer2_{ind}">
              </td>
            </tr>
            '''